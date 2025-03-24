pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'daboortocker/library_website'
        DOCKER_TAG = "latest"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/dabourt/library_website/'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t $DOCKER_IMAGE:$DOCKER_TAG ."
                }
            }
        }

        stage('Login to Docker Hub') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'DOCKER_HUB_PASSWORD', variable: 'DOCKER_PASS')]) {
                        sh "echo $DOCKER_PASS | docker login -u daboortocker --password-stdin"
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    sh "docker push $DOCKER_IMAGE:$DOCKER_TAG"
                }
            }
        }
    }
}
