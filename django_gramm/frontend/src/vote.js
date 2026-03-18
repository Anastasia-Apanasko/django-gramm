function vote(objType, objId, isLike) {
    const data = new FormData();
    if (objType === "post") data.append("post_pk", objId);
    else data.append("comment_pk", objId);
    data.append("is_like", isLike);

    fetch("/vote/", {
        method: "POST",
        body: data,
        headers: {
            "X-CSRFToken": csrftoken,
        },
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "ok") {
            if (objType === "post") {
                const likesEl = document.getElementById(`post-likes-count-${objId}`);
                const dislikesEl = document.getElementById(`post-dislikes-count-${objId}`);
                if (likesEl) likesEl.textContent = data.likes_count;
                if (dislikesEl) dislikesEl.textContent = data.dislikes_count;
            } else {
                const likesEl = document.getElementById(`comment-likes-count-${objId}`);
                const dislikesEl = document.getElementById(`comment-dislikes-count-${objId}`);
                if (likesEl) likesEl.textContent = data.likes_count;
                if (dislikesEl) dislikesEl.textContent = data.dislikes_count;
            }
        }
    })
    .catch(err => console.error("Error:", err));
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll(".like-btn").forEach(btn => {
        btn.addEventListener("click", function() {
            const objType = this.dataset.type;
            const objId = this.dataset.id;
            vote(objType, objId, true);
        });
    });

    document.querySelectorAll(".dislike-btn").forEach(btn => {
        btn.addEventListener("click", function() {
            const objType = this.dataset.type;
            const objId = this.dataset.id;
            vote(objType, objId, false);
        });
    });
});
