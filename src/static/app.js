document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  function showMessage(message, type) {
    messageDiv.textContent = message;
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
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const participants = Array.isArray(details.participants) ? details.participants : [];
        const spotsLeft = Math.max(details.max_participants - participants.length, 0);
        const participantsList = document.createElement("ul");
        participantsList.className = "participants-list";

        if (participants.length > 0) {
          participants.forEach((participant) => {
            const item = document.createElement("li");
            item.className = "participant-item";

            const participantLabel = document.createElement("span");
            participantLabel.textContent = participant;

            const removeButton = document.createElement("button");
            removeButton.type = "button";
            removeButton.className = "remove-participant";
            removeButton.dataset.activity = name;
            removeButton.dataset.email = participant;
            removeButton.title = `Désinscrire ${participant}`;
            removeButton.setAttribute("aria-label", `Désinscrire ${participant}`);
            removeButton.textContent = "×";

            item.appendChild(participantLabel);
            item.appendChild(removeButton);
            participantsList.appendChild(item);
          });
        } else {
          const emptyItem = document.createElement("li");
          emptyItem.className = "participant-empty";
          emptyItem.textContent = "Aucun participant pour le moment.";
          participantsList.appendChild(emptyItem);
        }

        const detailsContainer = document.createElement("div");
        detailsContainer.className = "participants-section";

        const participantsTitle = document.createElement("h5");
        participantsTitle.className = "participants-heading";
        participantsTitle.textContent = "Participants";
        participantsList.setAttribute("aria-label", "Participants de l’activité");

        const title = document.createElement("h4");
        title.textContent = name;

        const description = document.createElement("p");
        const descriptionLabel = document.createElement("strong");
        descriptionLabel.textContent = "Description:";
        description.appendChild(descriptionLabel);
        description.appendChild(document.createTextNode(` ${details.description}`));

        const schedule = document.createElement("p");
        const scheduleLabel = document.createElement("strong");
        scheduleLabel.textContent = "Schedule:";
        schedule.appendChild(scheduleLabel);
        schedule.appendChild(document.createTextNode(` ${details.schedule}`));

        const availability = document.createElement("p");
        const availabilityLabel = document.createElement("strong");
        availabilityLabel.textContent = "Availability:";
        availability.appendChild(availabilityLabel);
        availability.appendChild(document.createTextNode(` ${spotsLeft} spots left`));

        detailsContainer.appendChild(participantsTitle);
        detailsContainer.appendChild(participantsList);

        activityCard.appendChild(title);
        activityCard.appendChild(description);
        activityCard.appendChild(schedule);
        activityCard.appendChild(availability);
        activityCard.appendChild(detailsContainer);

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    if (!activity) {
      showMessage("Please select an activity.", "error");
      return;
    }

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
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  document.addEventListener("click", async (event) => {
    const button = event.target.closest(".remove-participant");
    if (!button) {
      return;
    }

    const activity = button.dataset.activity;
    const email = button.dataset.email;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        await fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to unregister the student.", "error");
      console.error("Error unregistering participant:", error);
    }
  });

  fetchActivities();
});
