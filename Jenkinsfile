pipeline {
    agent any

    environment {
        DOCKER_IMAGE_BACK_END = 'daboortocker/library_website'
        DOCKER_IMAGE_DATA_BASE = 'daboortocker/library_website_db'
        DOCKER_TAG = "latest"
        AWS_REGION = 'eu-west-1'
        DEPLOYMENT_NAME = "lib-db-deployment"
        NAMESPACE = "library-site"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/dabourt/library_website/'
            }
        }

        stage('Unit Tests') {
            steps {
                script {
                    sh """
                    cd backend_server

                    python3 -m venv venv
                    . venv/bin/activate

                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest

                    pytest tests/unit
                    """
                }
            }
        }

        stage('Build Backend Image') {
            steps {
                script {
                    sh "docker build -t $DOCKER_IMAGE_BACK_END:$DOCKER_TAG backend_server"
                }
            }
        }
        
        stage('Build Data-Base Image') {
            steps {
                script {
                    sh "docker build -t $DOCKER_IMAGE_DATA_BASE:$DOCKER_TAG db_server"
                }
            }
        }

        stage('Login to Docker Hub') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'DOCKER_HUB_PASSWORD', variable: 'DOCKER_PASS')]) {
                        sh "echo \$DOCKER_PASS | docker login -u daboortocker --password-stdin"
                    }
                }
            }
        }

        stage('Push Docker Images') {
            steps {
                script {
                    sh "docker push $DOCKER_IMAGE_BACK_END:$DOCKER_TAG"
                    sh "docker push $DOCKER_IMAGE_DATA_BASE:$DOCKER_TAG"
                }
            }
        }

        stage('Configure AWS Credentials') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credentials']]) {
                    sh 'aws sts get-caller-identity'
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    withAWS(credentials: 'aws-credentials', region: 'eu-west-1') {
                        sh 'aws eks update-kubeconfig --name my-eks-cluster --region eu-west-1'
                        
                        withKubeConfig([credentialsId: 'kubeconfig']) {
                            sh """

                            # Check if the namespace exists, create if not
                            kubectl get namespace $NAMESPACE || kubectl create namespace $NAMESPACE
                            kubectl config set-context --current --namespace=$NAMESPACE
                            
                            # Apply Kubernetes YAML configurations
                            kubectl apply -f lib_kube_config/lib-db-cluster-svc.yaml -n $NAMESPACE
                            kubectl apply -f lib_kube_config/lib-db-deployment.yaml -n $NAMESPACE
                            kubectl apply -f lib_kube_config/lib-db-pv.yaml -n $NAMESPACE
                            kubectl apply -f lib_kube_config/lib-db-pvc.yaml -n $NAMESPACE
                            kubectl apply -f lib_kube_config/lib-db-secret.yaml -n $NAMESPACE
                            kubectl apply -f lib_kube_config/lib-website-LB-scv.yaml -n $NAMESPACE
                            kubectl apply -f lib_kube_config/lib-website-deployment.yaml -n $NAMESPACE
                            kubectl apply -f lib_kube_config/lib-website-service.yaml -n $NAMESPACE
    
                            # Force fetch new image
                            kubectl rollout restart deployment/lib-web-deployment -n $NAMESPACE
                            kubectl rollout restart deployment/lib-db-deployment -n $NAMESPACE
    
                            # Verify that the deployment is running
                            kubectl get pods -n $NAMESPACE
                            """
                        }
                    }
                }
            }
        }
    }
}