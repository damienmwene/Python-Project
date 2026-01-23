pipeline {

  agent any

  stages {

    stage('SonarQube Code Analysis') {
      steps {
        withSonarQubeEnv('SonarQube') {
          withEnv(["SCANNER_HOME=${tool 'sonar-scanner'}"]) {
            sh '''
              $SCANNER_HOME/bin/sonar-scanner \
                -Dsonar.projectKey=uptime_monitor \
                -Dsonar.sources=.
            '''
          }
        }
      }
    }

    stage('Quality Gate') {
      steps {
        timeout(time: 1, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: false
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
