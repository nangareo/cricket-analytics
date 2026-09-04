import { test, expect, Page, Locator } from '@playwright/test';

/**
 * End-to-end checks for the Streamlit dashboard.
 *
 * Several of these guard specific bugs that shipped in the analytics layer:
 * batting average was previously strike rate ÷ 100, the bowling "wickets"
 * column was really the number of deliveries bowled, and Season Trends could
 * never render because the raw csv2 files were read with pd.read_csv.
 */

const TAB = {
  batting: 'BATTING',
  bowling: 'BOWLING',
  allRounders: 'ALL-ROUNDERS',
  headToHead: 'HEAD TO HEAD',
  seasonTrends: 'SEASON TRENDS',
  bestXI: 'BEST XI',
  playerSearch: 'PLAYER SEARCH',
  teamIntel: 'TEAM INTEL',
  liveScores: 'LIVE SCORES',
} as const;

/**
 * The panel the user is looking at.
 *
 * Streamlit keeps every panel in the DOM and marks inactive ones [hidden].
 * Team Intel nests a second tab set whose active panel is also un-hidden, so
 * filter on real visibility and take the outermost match.
 */
function activePanel(page: Page): Locator {
  return page.locator('[role="tabpanel"]:not([hidden]):visible').first();
}

/**
 * `exact` matters, and is case-sensitive: Team Intel's sub-tabs reuse these
 * names in title case ("Bowling" vs the top-level "BOWLING").
 */
async function openTab(page: Page, name: string) {
  await page.getByRole('tab', { name, exact: true }).click();
  await expect(activePanel(page)).toBeVisible();
}

/** Leaderboard rows, minus the header row that shares the .lb-row class. */
function leaderboardRows(page: Page): Locator {
  return activePanel(page).locator('.lb-row').filter({ has: page.locator('.lb-name') });
}

async function readRow(row: Locator) {
  const stats = await row.locator('.lb-stat').allInnerTexts();
  return {
    name: (await row.locator('.lb-name').innerText()).trim(),
    stats: stats.map((s) => parseFloat(s.replace(/[^0-9.\-]/g, ''))),
    score: parseFloat(await row.locator('.lb-score').innerText()),
  };
}

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  // First paint parses all 1243 match files, so wait on real content.
  await expect(page.getByRole('tab', { name: TAB.batting, exact: true })).toBeVisible();
  await expect(leaderboardRows(page).first()).toBeVisible();
});

test('all nine analysis tabs are available', async ({ page }) => {
  for (const name of Object.values(TAB)) {
    await expect(page.getByRole('tab', { name, exact: true })).toBeVisible();
  }
});

test('batting rankings report a real average, not strike rate over 100', async ({ page }) => {
  await openTab(page, TAB.batting);

  const rows = leaderboardRows(page);
  await expect(rows.first()).toBeVisible();

  for (const row of (await rows.all()).slice(0, 5)) {
    const { name, stats } = await readRow(row);
    const [runs, average, strikeRate] = stats;

    expect(runs, `${name} runs`).toBeGreaterThan(100);
    // A top-order T20 average sits well inside this band. The old bug put
    // every player between 1 and 3.
    expect(average, `${name} average`).toBeGreaterThan(10);
    expect(average, `${name} average`).toBeLessThan(100);
    // The signature of the bug: average === strike_rate / 100.
    expect(Math.abs(average - strikeRate / 100), `${name} avg vs sr/100`).toBeGreaterThan(1);
  }
});

test('bowling rankings report wickets, not deliveries bowled', async ({ page }) => {
  await openTab(page, TAB.bowling);

  const rows = leaderboardRows(page);
  await expect(rows.first()).toBeVisible();

  const wicketTallies: number[] = [];
  for (const row of (await rows.all()).slice(0, 10)) {
    const { name, stats } = await readRow(row);
    const [wickets, economy] = stats;

    // Nobody has taken 400 IPL wickets. The old column counted every ball,
    // which put the leaders in the hundreds and thousands.
    expect(wickets, `${name} wickets`).toBeGreaterThan(0);
    expect(wickets, `${name} wickets`).toBeLessThan(400);
    expect(economy, `${name} economy`).toBeGreaterThan(3);
    expect(economy, `${name} economy`).toBeLessThan(15);
    wicketTallies.push(wickets);
  }

  // Ball counts would all look alike; real wicket tallies vary a lot.
  expect(Math.max(...wicketTallies)).toBeGreaterThan(20);
});

test('season trends renders its charts instead of the raw-data warning', async ({ page }) => {
  await openTab(page, TAB.seasonTrends);

  const panel = activePanel(page);
  await expect(panel.locator('.js-plotly-plot').first()).toBeVisible();
  await expect(panel.locator('.js-plotly-plot')).toHaveCount(3);
  await expect(panel).not.toContainText('Raw data needed');
  // Season axis should span the full history.
  await expect(panel).toContainText('2026');
});

test('all-rounders tab lists players with both bat and ball records', async ({ page }) => {
  await openTab(page, TAB.allRounders);

  // This tab renders .player-card tiles rather than the .lb-row leaderboard.
  const cards = activePanel(page).locator('.player-card');
  await expect(cards.first()).toBeVisible();
  expect(await cards.count()).toBeGreaterThan(3);

  // Each card carries an all-rounder score; a broken merge would blank these.
  const score = parseFloat(await cards.first().locator('.player-score').innerText());
  expect(score).toBeGreaterThan(0);
  expect(score).toBeLessThanOrEqual(100);
});

test('team intel opens and exposes its sub-tabs', async ({ page }) => {
  await openTab(page, TAB.teamIntel);

  const panel = activePanel(page);
  await expect(panel.getByRole('tab', { name: 'SWOT', exact: true })).toBeVisible();
  await expect(panel.getByRole('tab', { name: 'Bowling', exact: true })).toBeVisible();
});

test('live scores tab renders without crashing', async ({ page }) => {
  await openTab(page, TAB.liveScores);

  const panel = activePanel(page);
  await expect(panel).toContainText('LIVE CRICKET SCORES');
  // Without a CRICAPI_KEY the tab reports a fetch failure rather than
  // throwing; either way Streamlit must not surface a Python traceback.
  await expect(panel).not.toContainText('Traceback');
});


test('every ranked player shows a real team, never "Unknown"', async ({ page }) => {
  // 186 players used to fall through a hand-maintained dict of 250 names.
  for (const tab of [TAB.batting, TAB.bowling, TAB.allRounders]) {
    await openTab(page, tab);
    await expect(activePanel(page)).not.toContainText('Unknown');
  }
});


test('Suryavanshi is shown as a Rajasthan Royal', async ({ page }) => {
  await openTab(page, TAB.batting);

  const row = leaderboardRows(page).filter({ hasText: 'V Suryavanshi' }).first();

  await expect(row).toContainText('Rajasthan Royals');
});


test('theme toggle switches the page between dark and light', async ({ page }) => {
  const ground = () =>
    page.evaluate(() =>
      getComputedStyle(document.documentElement).getPropertyValue('--bg').trim().toUpperCase(),
    );

  expect(await ground()).toBe('#0E1116');

  await page.getByText('Light', { exact: true }).click();
  await expect.poll(ground, { timeout: 30_000 }).toBe('#FAFAF8');

  // The choice must survive moving between tabs.
  await openTab(page, TAB.bowling);
  expect(await ground()).toBe('#FAFAF8');

  await page.getByText('Dark', { exact: true }).click();
  await expect.poll(ground, { timeout: 30_000 }).toBe('#0E1116');
});


test('no emoji remain in the top-level tab labels', async ({ page }) => {
  const labels = await page.getByRole('tab').allInnerTexts();
  const withEmoji = labels.filter((l) => /\p{Extended_Pictographic}/u.test(l));

  expect(withEmoji).toEqual([]);
});


/**
 * Contrast audit.
 *
 * Light mode originally shipped 30 elements below 3:1 — section titles, the
 * theme radio, widget labels, and score figures tinted with the team colour
 * (CSK yellow measured 1.46:1). This walks every visible text node in both
 * themes and measures it against its real painted background.
 */
async function lowContrastElements(page: Page) {
  // Audit the settled page: Streamlit's transient "Running..." chip is not a
  // steady state, and measuring mid-rerun reports it as a false positive.
  await expect(page.locator('[data-testid="stStatusWidget"]')).toHaveCount(0, {
    timeout: 30_000,
  });
  return page.evaluate(() => {
    const lum = (r: number, g: number, b: number) => {
      const f = (v: number) => {
        v /= 255;
        return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
      };
      return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
    };
    const parse = (c: string) => (c.match(/[\d.]+/g) || []).map(Number);
    const ratio = (fg: number[], bg: number[]) => {
      const a = lum(fg[0], fg[1], fg[2]);
      const b = lum(bg[0], bg[1], bg[2]);
      return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
    };
    const painted = (el: Element): number[] => {
      let n: Element | null = el;
      while (n && n !== document.documentElement) {
        const c = parse(getComputedStyle(n).backgroundColor);
        if (c.length >= 3 && (c[3] === undefined || c[3] > 0.5)) return c;
        n = n.parentElement;
      }
      return parse(getComputedStyle(document.body).backgroundColor);
    };

    const bad: { text: string; ratio: number; cls: string }[] = [];
    document.querySelectorAll('body *').forEach((el) => {
      const owns = [...el.childNodes].some(
        (n) => n.nodeType === 3 && n.textContent!.trim(),
      );
      if (el.children.length && !owns) return;
      const text = el.textContent!.trim();
      if (!text || text.length > 120) return;
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return;
      if (!(el as HTMLElement).offsetParent) return;
      const fg = parse(cs.color);
      if (fg.length < 3 || (fg[3] !== undefined && fg[3] < 0.1)) return;
      const r = ratio(fg, painted(el));
      if (r < 3.0) {
        bad.push({ text: text.slice(0, 40), ratio: +r.toFixed(2), cls: String(el.className).slice(0, 30) });
      }
    });
    return bad;
  });
}

test('no text falls below 3:1 contrast in either theme', async ({ page }) => {
  expect(await lowContrastElements(page)).toEqual([]);

  await page.getByText('Light', { exact: true }).click();
  await expect
    .poll(
      () =>
        page.evaluate(() =>
          getComputedStyle(document.documentElement)
            .getPropertyValue('--bg')
            .trim()
            .toUpperCase(),
        ),
      { timeout: 30_000 },
    )
    .toBe('#FAFAF8');

  expect(await lowContrastElements(page)).toEqual([]);
});


test('the page requests no third-party resources', async ({ page }) => {
  // Everything must be free and work offline: no webfont CDN, no trackers.
  // The only outbound call the app makes is the optional live-scores API.
  const external: string[] = [];
  page.on('request', (r) => {
    const url = new URL(r.url());
    if (!['localhost', '127.0.0.1'].includes(url.hostname)) external.push(url.hostname);
  });

  await page.goto('/');
  await expect(leaderboardRows(page).first()).toBeVisible();

  expect([...new Set(external)]).toEqual([]);
});


/**
 * Chart marks must stay visible.
 *
 * The sequential ramps originally ran their quiet end down to 1.19:1 against
 * the surface, which left the shortest bars all but invisible. These bars are
 * discrete ordered marks, one per player, so every step has to clear the
 * ordinal floor of 2:1 — not just the deepest one.
 */
async function faintestBarContrast(page: Page) {
  // Switching theme reruns the script: the CSS variables flip immediately but
  // Plotly repaints a moment later, so an eager read measures the previous
  // theme's marks against the new surface.
  await expect(page.locator('[data-testid="stStatusWidget"]')).toHaveCount(0, {
    timeout: 30_000,
  });
  return page.evaluate(() => {
    const lum = (r: number, g: number, b: number) => {
      const f = (v: number) => {
        v /= 255;
        return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
      };
      return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
    };
    const parse = (c: string) => (c.match(/[\d.]+/g) || []).map(Number);
    const surf = parse(getComputedStyle(document.body).backgroundColor);
    const panel = [...document.querySelectorAll('[role="tabpanel"]')].find(
      (p) => !p.hasAttribute('hidden') && (p as HTMLElement).offsetParent !== null,
    );
    if (!panel) return null;
    const marks = [...panel.querySelectorAll('.plot .point path, .plot .bars path')];
    if (!marks.length) return null;
    let worst: { ratio: number; fill: string; chart: string } | null = null;
    for (const el of marks) {
      const f = (el as SVGElement).style.fill || el.getAttribute('fill');
      if (!f) continue;
      const c = parse(f);
      const a = lum(c[0], c[1], c[2]);
      const b = lum(surf[0], surf[1], surf[2]);
      const ratio = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
      if (!worst || ratio < worst.ratio) {
        worst = {
          ratio,
          fill: f,
          chart: (el.closest('.js-plotly-plot')?.querySelector('.gtitle')?.textContent || '?').slice(0, 40),
        };
      }
    }
    return worst;
  });
}

for (const theme of ['dark', 'light'] as const) {
  test(`every chart bar stays visible against the ${theme} surface`, async ({ page }) => {
    if (theme === 'light') {
      await page.getByText('Light', { exact: true }).click();
      await expect
        .poll(
          () =>
            page.evaluate(() =>
              getComputedStyle(document.documentElement)
                .getPropertyValue('--bg')
                .trim()
                .toUpperCase(),
            ),
          { timeout: 30_000 },
        )
        .toBe('#FAFAF8');
    }

    for (const tab of [TAB.batting, TAB.bowling, TAB.seasonTrends]) {
      await openTab(page, tab);
      await expect(activePanel(page).locator('.js-plotly-plot').first()).toBeVisible();
      // Poll rather than read once: Plotly repaints asynchronously after the
      // rerun, so the first read can still hold the old theme's marks.
      await expect
        .poll(async () => (await faintestBarContrast(page))?.ratio ?? 0, {
          timeout: 30_000,
        })
        .toBeGreaterThanOrEqual(2);

      const faintest = await faintestBarContrast(page);
      expect(
        faintest!.ratio,
        `${tab}: "${faintest!.chart}" mark ${faintest!.fill} on the ${theme} surface`,
      ).toBeGreaterThanOrEqual(2);
    }
  });
}


test('batting and bowling charts use different materials', async ({ page }) => {
  // The bat is willow, the ball is leather. Both are red-dominant in RGB, so
  // compare hue angle rather than which channel wins.
  const hue = async (tab: string) => {
    await openTab(page, tab);
    await expect(activePanel(page).locator('.js-plotly-plot').first()).toBeVisible();
    return page.evaluate(() => {
      const panel = [...document.querySelectorAll('[role="tabpanel"]')].find(
        (p) => !p.hasAttribute('hidden') && (p as HTMLElement).offsetParent !== null,
      )!;
      const fills = [...panel.querySelectorAll('.plot .point path, .plot .bars path')]
        .map((el) => (el as SVGElement).style.fill)
        .filter(Boolean) as string[];
      const [r, g, b] = (fills[0].match(/[\d.]+/g) || []).map(Number).map((v) => v / 255);
      const max = Math.max(r, g, b);
      const min = Math.min(r, g, b);
      const d = max - min;
      if (!d) return 0;
      let h: number;
      if (max === r) h = ((g - b) / d) % 6;
      else if (max === g) h = (b - r) / d + 2;
      else h = (r - g) / d + 4;
      return ((h * 60) + 360) % 360;
    });
  };

  const willow = await hue(TAB.batting);
  const leather = await hue(TAB.bowling);

  // Amber sits around 40 degrees, leather red around 10.
  expect(Math.abs(willow - leather), `willow ${willow} vs leather ${leather}`)
    .toBeGreaterThan(15);
});


/**
 * Green is reserved for grass.
 *
 * It survives in exactly two places: the Season Trends charts (the ground over
 * time) and the faint pitch wash behind the header. Everywhere else the
 * interface is neutral — active states carry weight and ink, not hue.
 */
async function greenUiElements(page: Page) {
  return page.evaluate(() => {
    const parse = (c: string) => (c.match(/[\d.]+/g) || []).map(Number);
    const isGreen = (c: string) => {
      const p = parse(c);
      if (p.length < 3) return false;
      if (p[3] !== undefined && p[3] < 0.02) return false;
      const [r, g, b] = p;
      if (Math.max(r, g, b) - Math.min(r, g, b) < 25) return false;
      return g === Math.max(r, g, b) && g - Math.max(r, b) > 15;
    };
    const found: string[] = [];
    document.querySelectorAll('body *').forEach((el) => {
      if (el.closest('.js-plotly-plot')) return; // charts are allowed colour
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || !(el as HTMLElement).offsetParent) return;
      for (const prop of ['color', 'backgroundColor', 'borderBottomColor'] as const) {
        if (cs[prop] && isGreen(cs[prop])) {
          found.push(`${String(el.className).slice(0, 24)}:${prop}=${cs[prop]}`);
          break;
        }
      }
    });
    return found;
  });
}

test('the interface carries no green outside the charts', async ({ page }) => {
  expect(await greenUiElements(page)).toEqual([]);

  await page.getByText('Light', { exact: true }).click();
  await expect
    .poll(
      () =>
        page.evaluate(() =>
          getComputedStyle(document.documentElement)
            .getPropertyValue('--bg')
            .trim()
            .toUpperCase(),
        ),
      { timeout: 30_000 },
    )
    .toBe('#FAFAF8');

  expect(await greenUiElements(page)).toEqual([]);
});


test('green is kept for the pitch and for Season Trends', async ({ page }) => {
  // The pitch wash behind the header.
  const heroBg = await page
    .locator('.hero')
    .evaluate((el) => getComputedStyle(el).backgroundImage);
  expect(heroBg).toMatch(/rgba?\(\s*(47,\s*190,\s*140|15,\s*122,\s*85)/);

  // Season Trends is the one tab whose marks stay green.
  await openTab(page, TAB.seasonTrends);
  await expect(activePanel(page).locator('.js-plotly-plot').first()).toBeVisible();
  const greenMarks = await page.evaluate(() => {
    const panel = [...document.querySelectorAll('[role="tabpanel"]')].find(
      (p) => !p.hasAttribute('hidden') && (p as HTMLElement).offsetParent !== null,
    )!;
    const fills = [...panel.querySelectorAll('.plot .point path, .plot .bars path')]
      .map((e) => (e as SVGElement).style.fill)
      .filter(Boolean) as string[];
    return fills.filter((f) => {
      const [r, g, b] = (f.match(/[\d.]+/g) || []).map(Number);
      return g === Math.max(r, g, b) && g - Math.max(r, b) > 15;
    }).length;
  });
  expect(greenMarks).toBeGreaterThan(0);
});


test('batting and Best XI charts carry no green', async ({ page }) => {
  for (const tab of [TAB.batting, TAB.bowling, TAB.bestXI]) {
    await openTab(page, tab);
    await expect(activePanel(page).locator('.js-plotly-plot').first()).toBeVisible();
    const green = await page.evaluate(() => {
      const panel = [...document.querySelectorAll('[role="tabpanel"]')].find(
        (p) => !p.hasAttribute('hidden') && (p as HTMLElement).offsetParent !== null,
      )!;
      return [...panel.querySelectorAll('.plot .point path, .plot .bars path')]
        .map((e) => (e as SVGElement).style.fill)
        .filter(Boolean)
        .filter((f) => {
          const [r, g, b] = (f!.match(/[\d.]+/g) || []).map(Number);
          return g === Math.max(r, g, b) && g - Math.max(r, b) > 15;
        }).length;
    });
    expect(green, `${tab} green marks`).toBe(0);
  }
});


/**
 * Each analysis tab must be tellable apart by its chart colour.
 *
 * Season Trends and Best XI originally shared turf green and sightscreen sky,
 * which measured ΔE 13.2-15.0 apart in dark and 9.3 in light — below the 15
 * floor, i.e. hard to distinguish even with full colour vision. Best XI now
 * uses indigo. This measures the rendered marks, in OKLab, the way the palette
 * validator does.
 */
const OKLAB_FLOOR = 15;

async function dominantChartColour(page: Page, tab: string) {
  await openTab(page, tab);
  await expect(activePanel(page).locator('.js-plotly-plot').first()).toBeVisible();
  await expect(page.locator('[data-testid="stStatusWidget"]')).toHaveCount(0, {
    timeout: 30_000,
  });
  return page.evaluate(() => {
    const panel = [...document.querySelectorAll('[role="tabpanel"]')].find(
      (p) => !p.hasAttribute('hidden') && (p as HTMLElement).offsetParent !== null,
    )!;
    const fills = [...panel.querySelectorAll('.plot .point path, .plot .bars path')]
      .map((e) => (e as SVGElement).style.fill)
      .filter(Boolean) as string[];
    const weight = (f: string) => {
      const [r, g, b] = (f.match(/[\d.]+/g) || []).map(Number);
      return r + g + b;
    };
    // the ramp's dominant end, i.e. the colour the tab reads as
    return [...new Set(fills)].sort((a, b) => weight(b) - weight(a))[0];
  });
}

function deltaE(a: string, b: string) {
  const oklab = (c: string) => {
    let [r, g, bl] = (c.match(/[\d.]+/g) || []).map(Number).slice(0, 3).map((v) => v / 255);
    const f = (v: number) => (v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4));
    r = f(r); g = f(g); bl = f(bl);
    const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * bl);
    const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * bl);
    const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * bl);
    return [
      0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s,
      1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s,
      0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s,
    ];
  };
  const [A, B] = [oklab(a), oklab(b)];
  return 100 * Math.hypot(A[0] - B[0], A[1] - B[1], A[2] - B[2]);
}

test('each tab is tellable apart by its chart colour', async ({ page }) => {
  const tabs = [TAB.batting, TAB.bowling, TAB.seasonTrends, TAB.bestXI];
  const seen: Record<string, string> = {};
  for (const t of tabs) seen[t] = await dominantChartColour(page, t);

  for (let i = 0; i < tabs.length; i++) {
    for (let j = i + 1; j < tabs.length; j++) {
      const d = deltaE(seen[tabs[i]], seen[tabs[j]]);
      expect(
        d,
        `${tabs[i]} (${seen[tabs[i]]}) vs ${tabs[j]} (${seen[tabs[j]]}) — ΔE ${d.toFixed(1)}`,
      ).toBeGreaterThanOrEqual(OKLAB_FLOOR);
    }
  }
});


/**
 * Season Trends.
 *
 * It previously drew two bar charts on a time axis, coloured each bar by its
 * own value (double-encoding bar length as hue), and printed a number above
 * all nineteen bars. It also divided runs by matches rather than innings and
 * left extras out, which put "average team score" at roughly twice a real
 * T20 total.
 */
test('season trends draws trends as lines, not value-ramped bars', async ({ page }) => {
  await openTab(page, TAB.seasonTrends);
  const panel = activePanel(page);
  await expect(panel.locator('.js-plotly-plot').first()).toBeVisible();

  const shape = await page.evaluate(() => {
    const p = [...document.querySelectorAll('[role="tabpanel"]')].find(
      (x) => !x.hasAttribute('hidden') && (x as HTMLElement).offsetParent !== null,
    )!;
    return [...p.querySelectorAll('.js-plotly-plot')].map((c) => ({
      title: c.querySelector('.gtitle')?.textContent ?? '',
      lines: c.querySelectorAll('.scatterlayer .trace .js-line').length,
      bars: c.querySelectorAll('.barlayer .point path').length,
      barColours: new Set(
        [...c.querySelectorAll('.barlayer .point path')].map((e) => (e as SVGElement).style.fill),
      ).size,
      pointLabels: [...c.querySelectorAll('.scatterlayer text')].filter((t) =>
        t.textContent!.trim(),
      ).length,
    }));
  });

  const trends = shape.filter((c) => c.lines > 0);
  expect(trends.length, 'the two trends are drawn as lines').toBe(2);

  for (const c of trends) {
    // Labels ride the endpoints and the peak only — never all 19 seasons.
    expect(c.pointLabels, `${c.title} labels`).toBeLessThanOrEqual(3);
    expect(c.pointLabels, `${c.title} labels`).toBeGreaterThan(0);
  }

  for (const c of shape.filter((x) => x.bars > 0)) {
    // One series, one colour: bar length already carries the value.
    expect(c.barColours, `${c.title} bar colours`).toBe(1);
  }
});


test('season trends reports a believable team score', async ({ page }) => {
  await openTab(page, TAB.seasonTrends);
  await expect(activePanel(page).locator('.js-plotly-plot').first()).toBeVisible();

  const labels = await page.evaluate(() => {
    const p = [...document.querySelectorAll('[role="tabpanel"]')].find(
      (x) => !x.hasAttribute('hidden') && (x as HTMLElement).offsetParent !== null,
    )!;
    const chart = [...p.querySelectorAll('.js-plotly-plot')].find((c) =>
      /team score/i.test(c.querySelector('.gtitle')?.textContent ?? ''),
    )!;
    return [...chart.querySelectorAll('.scatterlayer text')]
      .map((t) => parseFloat(t.textContent!))
      .filter((n) => !Number.isNaN(n));
  });

  expect(labels.length).toBeGreaterThan(0);
  for (const v of labels) {
    // A T20 innings, not both innings added together.
    expect(v, `team score ${v}`).toBeGreaterThan(110);
    expect(v, `team score ${v}`).toBeLessThan(230);
  }
});
