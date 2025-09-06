### README.md

# Nemo\_techseries

## 💡 Solution Overview

The `Nemo_techseries` project addresses the challenge of social isolation among Singapore's migrant worker community. With a significant portion of the workforce being foreign workers, a key problem is the fragmented communication channels used by various organizations (like MOM and NGOs) to promote events. This often leads to migrant workers missing out on valuable community activities.

Our solution is a centralized platform designed to complement existing services like FWMOMCare by offering a single, accessible interface for discovering and engaging in community-driven events.

### Key Features

  * **Facility & Workshop Browsing:** A collated, multi-lingual list of community events from different organizations, simplifying the discovery process. Users can filter activities based on their preferences.
  * **Activity Sign-up & Team Formation:** Users can sign up for events individually or with friends, fostering peer connections and encouraging group participation.

### Unique Selling Points

  * **Community-Centric:** Unlike existing one-way service apps, our platform is built around social interaction and community building, emphasizing who you can do activities with.
  * **Empowerment:** The app encourages users to be proactive in their social lives rather than just consuming services.
  * **Integrated Wellness:** It combines physical health (facility booking), mental health (social connection), and personal growth (workshops) into a single, easy-to-use experience.

## ⚙️ Solution Architecture

The project follows a monolithic architecture for streamlined deployment, with a clear separation of concerns between the frontend and backend.

  * **Frontend:** Built with **Vue.js**, chosen for its ease of use and flexibility.
  * **Backend:** Developed using **Flask**, a lightweight and minimal Python framework, which exposes a **RESTful API** for the frontend to consume JSON data.

This architecture provides a solid foundation for future scalability, with considerations for transitioning to a cloud infrastructure using Docker and Kubernetes.

## ▶️ Run Instructions

To get the application up and running locally, you will need to set up both the frontend and the backend.

### Prerequisites

Ensure you have the following installed on your machine:

  * **Node.js & npm:** For the Vue.js frontend.
  * **Python 3.x:** For the Flask backend.

### Step-by-Step Guide

1.  **Clone the repository:**

    ```sh
    git clone https://github.com/your-username/Nemo_techseries.git
    cd Nemo_techseries
    ```

2.  **Add Firebase Secret Files:**
    The application relies on Firebase for its backend. You need to copy the following four files into the `NemoApp/firebase` folder:

      * `firebase-admin-key.json`
      * `firebase-config.js`
      * `firestore.indexes.json`
      * `firestore.rules`

3.  **Set up the Frontend:**
    Navigate to the `frontend` directory, install the dependencies, and start the development server.

    ```sh
    cd NemoApp/frontend
    npm install
    npm run dev
    ```

    The frontend will be accessible at `http://localhost:5173` (or the port specified by Vue).

4.  **Set up the Backend:**
    Open a new terminal, navigate to the `backend` directory, and start the Flask application.

    ```sh
    cd NemoApp/backend
    python app.py
    ```

    The backend will run on `http://127.0.0.1:5000` by default.

With both the frontend and backend running, you can now interact with the application. The Vue.js frontend will automatically communicate with the Flask backend via the RESTful API to retrieve event data.