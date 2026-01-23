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
        timeout(time: 5, unit: 'MINUTES') {
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
        script {
          docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-creds') {
            docker.image("mwene/uptime_monitor:v2").push()
          }
        }
      }
    }
  }
}
