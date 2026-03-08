pipeline {
    agent any

    environment {
        IMAGE_NAME     = "cricket-analytics"
        CONTAINER_NAME = "cricket-dashboard"
        PORT           = "8501"
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
                sh 'docker build -t ${IMAGE_NAME}:latest .'
            }
        }

        stage('Stop Old Container') {
            steps {
                echo '🛑 Stopping old container...'
                sh 'docker stop ${CONTAINER_NAME} || true'
                sh 'docker rm ${CONTAINER_NAME} || true'
            }
        }

        stage('Run New Container') {
            steps {
                echo '🚀 Starting new container...'
                sh '''
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        --restart always \
                        -p ${PORT}:8501 \
                        -v /home/ubuntu/cricket-data:/app/data \
                        ${IMAGE_NAME}:latest \
                        streamlit run dashboard/app.py \
                        --server.port=8501 \
                        --server.address=0.0.0.0
                '''
            }
        }

        stage('Verify') {
            steps {
                echo '✅ Verifying container is running...'
                sh 'docker ps | grep ${CONTAINER_NAME}'
            }
        }
    }

    post {
        success {
            echo '🎉 Deployment successful! Dashboard live at http://13.126.172.252:8501'
        }
        failure {
            echo '❌ Deployment failed! Check logs above.'
        }
    }
}