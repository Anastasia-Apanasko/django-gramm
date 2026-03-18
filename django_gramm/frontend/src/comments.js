document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll(".comment-form").forEach(form => {
        form.addEventListener("submit", function (e) {
            e.preventDefault();

            console.log("COMMENT SUBMIT");


            const postId = this.dataset.postId;
            const contentInput = this.querySelector("textarea[name='text']");
            const content = contentInput.value.trim();
            if (!content) return;

            const data = new FormData();
            data.append("content", content);
            const url = this.dataset.url;

            fetch(url, {
                method: "POST",
                body: data,
                headers: {"X-CSRFToken": csrftoken},
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "ok") {
                        const commentsContainer = document.getElementById(`comments-${postId}`);
                        const newComment = document.createElement("div");
                        newComment.classList.add("comment");
                        newComment.id = `comment-${data.id}`;
                        newComment.innerHTML = `
                          <strong>
                            <a href="/users/${data.author}/">${data.author}</a>
                          </strong>:
                          <span>${data.content}</span>
                          <br>
                          <small class="text-muted">${data.created_at}</small>
                        
                          <div class="d-flex mt-1">
                              <button class="btn btn-sm btn-outline-success like-btn" data-type="comment" data-id="${data.id}">
                                  👍 <span id="comment-likes-count-${data.id}">0</span>
                              </button>
                              <button class="btn btn-sm btn-outline-danger dislike-btn" data-type="comment" data-id="${data.id}">
                                  👎 <span id="comment-dislikes-count-${data.id}">0</span>
                              </button>
                          </div>
                        `;

                        commentsContainer.appendChild(newComment);
                        contentInput.value = "";
                    } else {
                        alert(data.message);
                    }
                })
                .catch(err => console.error("Error:", err));
        });
    });
});
