pipeline {
    agent any

    environment {
        IMAGE = "sbe03011/django_project"
        TAG = "v${env.BUILD_NUMBER}"
        DEPLOY_FILE = "k8s/deployment.yaml"
    }
    stage('Cleanup') {
	steps {
        	deleteDir()
    	}
    }

    stages {
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/OhseungKeun/project_app.git',
                        credentialsId: 'Github-Token'
                    ]]
                ])
            }
        }


        stage('Build Docker Image') {
            steps {
                sh """
                docker build -t $IMAGE:$TAG .
                """
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([string(credentialsId: 'dockerhub-password', variable: 'DOCKER_PW')]) {
                    sh """
                    docker login -u sbe03011 -p $DOCKER_PW
                    docker push $IMAGE:$TAG
                    """
                }
            }
        }

        stage('Update Manifest') {
            steps {
                withCredentials([string(credentialsId: 'Git-Token', variable: 'GIT_TOKEN')]) {
                    sh """
                    git config user.email "sbe03011@naver.com"
                    git config user.name "OhseungKeun"

                    git checkout main
		    git pull --rebase origin main

                    sed -i "s|image:.*|image: $IMAGE:$TAG|g" $DEPLOY_FILE

                    git add $DEPLOY_FILE
                    git commit -m "Update image to $IMAGE:$TAG" || true

		    git fetch origin main
                    git push -f https://$GIT_TOKEN@github.com/OhseungKeun/argocd.git main
                    """
                }
            }
        }
    }
}
