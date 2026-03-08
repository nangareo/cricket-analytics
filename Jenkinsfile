pipeline {
    agent any

    environment {
        IMAGE_NAME     = "cricket-analytics"
        CONTAINER_NAME = "cricket-dashboard"
        PORT           = "8501"
        ECR_URI        = "526002960065.dkr.ecr.ap-south-1.amazonaws.com/cricket-analytics:latest"
        AWS_REGION     = "ap-south-1"
        ECR_REGISTRY   = "526002960065.dkr.ecr.ap-south-1.amazonaws.com"
    }

    stages {
        stage('Checkout') {
            steps {
                echo '📥 Pulling latest code from GitHub...'
                checkout scm
            }
        }

        stage('Pull from ECR') {
            steps {
                echo '📦 Pulling Docker image from ECR...'
                withCredentials([
                    string(credentialsId: 'AWS_ACCESS_KEY_ID',     variable: 'AWS_KEY'),
                    string(credentialsId: 'AWS_SECRET_ACCESS_KEY', variable: 'AWS_SECRET')
                ]) {
                    sh '''
                        export AWS_ACCESS_KEY_ID=$AWS_KEY
                        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET
                        export AWS_DEFAULT_REGION=ap-south-1
                        aws ecr get-login-password --region ap-south-1 | \
                        docker login --username AWS --password-stdin 526002960065.dkr.ecr.ap-south-1.amazonaws.com
                        docker pull 526002960065.dkr.ecr.ap-south-1.amazonaws.com/cricket-analytics:latest
                        docker tag  526002960065.dkr.ecr.ap-south-1.amazonaws.com/cricket-analytics:latest cricket-analytics:latest
                    '''
                }
            }
        }

        stage('Stop Old Container') {
            steps {
                echo '🛑 Stopping old container...'
                sh 'docker stop ${CONTAINER_NAME} || true'
                sh 'docker rm   ${CONTAINER_NAME} || true'
            }
        }

        stage('Run New Container') {
            steps {
                echo '🚀 Starting new container...'
                sh '''
                    docker run -d \
                        --name cricket-dashboard \
                        --restart always \
                        -p 8501:8501 \
                        -v /home/ubuntu/cricket-data:/app/data \
                        cricket-analytics:latest \
                        streamlit run dashboard/app.py \
                        --server.port=8501 \
                        --server.address=0.0.0.0
                '''
            }
        }

        stage('Verify') {
            steps {
                echo '✅ Verifying container is running...'
                sh 'docker ps | grep cricket-dashboard'
            }
        }
    }

    post {
        success {
            echo '🎉 Dashboard live at http://13.126.172.252:8501'
        }
        failure {
            echo '❌ Deployment failed! Check logs above.'
        }
    }
}