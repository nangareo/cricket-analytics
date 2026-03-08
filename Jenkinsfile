pipeline {
    agent any

    environment {
        IMAGE_NAME     = "cricket-analytics"
        CONTAINER_NAME = "cricket-dashboard"
        PORT           = "8501"
        ECR_URI        = "526002960065.dkr.ecr.ap-south-1.amazonaws.com/cricket-analytics:latest"
        AWS_REGION     = "ap-south-1"
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
                sh 'aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin 526002960065.dkr.ecr.ap-south-1.amazonaws.com'
                sh 'docker pull ${ECR_URI}'
                sh 'docker tag ${ECR_URI} ${IMAGE_NAME}:latest'
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
            echo '🎉 Dashboard live at http://13.126.172.252:8501'
        }
        failure {
            echo '❌ Deployment failed! Check logs above.'
        }
    }
}