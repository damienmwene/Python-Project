pipeline {
  agent any

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('SonarQube Analysis') {
      steps {
        script {
          def scannerHome = tool 'sonar-scanner'

          withSonarQubeEnv('SonarQube') {
            withCredentials([string(credentialsId: 'jenkins-sonar-token-2', variable: 'SONAR_TOKEN')]) {

              sh """
              ${scannerHome}/bin/sonar-scanner \
              -Dsonar.projectKey=uptime_monitor \
              -Dsonar.sources=. \
              -Dsonar.token=$SONAR_TOKEN
              """
            }
          }
        }
      }
    }

    stage('Quality Gate') {
      steps {
        timeout(time: 10, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: true
        }
      }
    }

    stage('Docker Build') {
      steps {
        sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."
      }
    }

    stage('Docker Push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh """
          echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
          docker push ${IMAGE_NAME}:${BUILD_NUMBER}
          """
        }
      }
    }

    stage('Update Helm Chart') {
      steps {
        sh '''
        sed -i "s/tag:.*/tag: \\"${BUILD_NUMBER}\\"/" uptime-monitor-chart/values.yaml
        git add uptime-monitor-chart/values.yaml
        git commit -m "Update image tag to ${BUILD_NUMBER}"
        git push
        '''
      }
    }
  }
}
