document.addEventListener("DOMContentLoaded", () => {
    const followButtons = document.querySelectorAll(".follow-btn, .unfollow-btn");

    followButtons.forEach(button => {
        button.addEventListener("click", async (e) => {
            e.preventDefault();
            const url = button.dataset.url;

            try {
                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrftoken,
                        "Accept": "application/json",
                    },
                });

                if (response.ok) {
                    const data = await response.json();

                    if (data.status === "followed") {
                        button.textContent = "Unfollow";
                        button.classList.remove("btn-success");
                        button.classList.add("btn-outline-danger");
                        button.dataset.url = data.unfollow_url;
                    } else if (data.status === "unfollowed") {
                        button.textContent = "Follow";
                        button.classList.remove("btn-outline-danger");
                        button.classList.add("btn-success");
                        button.dataset.url = data.follow_url;
                    }
                }
            } catch (error) {
                console.error("Error:", error);
            }
        });
    });
});
