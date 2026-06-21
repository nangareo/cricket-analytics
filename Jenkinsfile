pipeline {
    agent any

    environment {
        DOCKERHUB_USER  = "omkarnangare"
        IMAGE_NAME      = "cricket-analytics"
        CONTAINER_NAME  = "cricket-dashboard"
        IMAGE_TAG       = "${DOCKERHUB_USER}/${IMAGE_NAME}:latest"
        IMAGE_TAG_BUILD = "${DOCKERHUB_USER}/${IMAGE_NAME}:build-${BUILD_NUMBER}"
        PORT            = "8501"
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {

        stage('Checkout') {
            steps {
                echo '📥 Pulling latest code from GitHub...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                sh """
                    docker build -t ${IMAGE_TAG} -t ${IMAGE_TAG_BUILD} .
                """
            }
        }

        stage('Test') {
            steps {
                echo '✅ Running basic smoke test on image...'
                sh """
                    docker run --rm ${IMAGE_TAG} python -c "import streamlit, pandas, plotly; print('Imports OK')"
                """
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo '📤 Pushing image to Docker Hub...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DH_USER',
                    passwordVariable: 'DH_PASS'
                )]) {
                    sh """
                        echo \$DH_PASS | docker login -u \$DH_USER --password-stdin
                        docker push ${IMAGE_TAG}
                        docker push ${IMAGE_TAG_BUILD}
                    """
                }
            }
        }

        stage('Deploy') {
            steps {
                echo '🚀 Deploying new container...'
                sh """
                    docker pull ${IMAGE_TAG}
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} --restart always \
                        -p ${PORT}:${PORT} \
                        -v /home/ubuntu/cricket-data:/app/data \
                        ${IMAGE_TAG}
                """
            }
        }

        stage('Verify') {
            steps {
                echo '🔍 Verifying deployment...'
                sh """
                    sleep 5
                    docker ps | grep ${CONTAINER_NAME}
                """
            }
        }

        stage('Cleanup') {
            steps {
                echo '🧹 Removing dangling images...'
                sh 'docker image prune -f'
            }
        }
    }

    post {
        success {
            echo '🎉 Deployment successful! Dashboard live at http://13.126.172.252:8501'
        }
        failure {
            echo '❌ Pipeline failed — check logs above.'
        }
        always {
            sh 'docker logout || true'
        }
    }
}