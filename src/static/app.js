document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  function showMessage(text, type = "success") {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Sélectionnez une activité --</option>';

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const participants = details.participants || [];
        const spotsLeft = Math.max(details.max_participants - participants.length, 0);
        const participantItems = participants.length
          ? participants
              .map(
                (email) => `
                  <li>
                    ${email}
                    <button
                      type="button"
                      class="remove-participant"
                      data-activity="${name}"
                      data-email="${email}"
                    >
                      Supprimer
                    </button>
                  </li>
                `
              )
              .join("")
          : "<li>Aucun participant pour le moment.</li>";

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Horaire :</strong> ${details.schedule}</p>
          <p><strong>Disponibilité :</strong> ${spotsLeft} place(s) restante(s)</p>
          <div class="participants-section">
            <strong>Participants :</strong>
            <ul class="participants-list">${participantItems}</ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      document.querySelectorAll(".remove-participant").forEach((button) => {
        button.addEventListener("click", async () => {
          const activity = button.dataset.activity;
          const email = button.dataset.email;

          try {
            const response = await fetch(
              `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
              { method: "DELETE" }
            );
            const result = await response.json();

            if (response.ok) {
              showMessage(result.message, "success");
              await fetchActivities();
            } else {
              showMessage(result.detail || "Impossible de désinscrire l'élève.", "error");
            }
          } catch (error) {
            console.error("Erreur lors de la désinscription de l'élève :", error);
            showMessage("Impossible de désinscrire l'élève.", "error");
          }
        });
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Impossible de charger les activités. Veuillez réessayer plus tard.</p>";
      console.error("Erreur lors du chargement des activités :", error);
    }
  }

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        await fetchActivities();
      } else {
        showMessage(result.detail || "Une erreur s'est produite.", "error");
      }
    } catch (error) {
      showMessage("Impossible de vous inscrire. Veuillez réessayer.", "error");
      console.error("Erreur lors de l'inscription :", error);
    }
  });

  fetchActivities();
});
