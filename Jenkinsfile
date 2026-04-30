pipeline {

  agent any

  stages {

    stage('SonarQube Code Analysis') {
        steps {
            script {
                def scannerHome = tool 'sonar-scanner'
                withSonarQubeEnv('SonarQube') {
                    sh """
                    ${scannerHome}/bin/sonar-scanner \
                    -Dsonar.projectKey=uptime_monitor \
                    -Dsonar.sources=. \
                    -Dsonar.host.url=http://localhost:9000 \
                    -Dsonar.login=${SONAR_TOKEN}
                    """
                }
            }
        }
    }

    stage('Quality Gate') {
      steps {
        timeout(time: 1, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: true
        }
      }
    }

    stage('Docker Build') {
      steps {
        sh "docker build -t ${IMAGE_NAME}:v2 ."
      }
    }

    stage('Docker Push') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub-creds',
        )]) {
          sh """
          docker login -u --password-stdin
          docker push ${IMAGE_NAME}:v2
          """
        }
      }
    }
  }
}
