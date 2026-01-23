pipeline {

  agent any

  stages {

    stage('SonarQube Code Analysis') {
      steps {
        withSonarQubeEnv('SonarQube') {
        withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
          withEnv(["SCANNER_HOME=${tool 'sonar-scanner'}"]) {
          sh """
          $SCANNER_HOME/bin/sonar-scanner \
            -Dsonar.projectKey=uptime_monitor \
            -Dsonar.sources=. \
            -Dsonar.host.url=${SONAR_HOST_URL} \
            -Dsonar.token=${SONAR_TOKEN}
          """
          }
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
