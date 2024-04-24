function getCookie(name) {
  let cookie = document.cookie.split('; ').find(row => row.startsWith(name + '='));
  return cookie ? cookie.split('=')[1] : null;
}
const commentForm = document.forms.commentForm;
const commentFormContent = commentForm.content;
const commentFormParentInput = commentForm.parent;
const commentFormSubmit = commentForm.commentSubmit;
const commentPostId = commentForm.getAttribute('data-post-id');

commentForm.addEventListener('submit', createComment);

replyUser();
listenDeleteBtn();

function replyUser() {
  document.querySelectorAll('.btn-reply').forEach(e => {
    e.addEventListener('click', replyComment);
  });
}

function replyComment() {
  const commentUsername = this.getAttribute('data-comment-username');
  const commentMessageId = this.getAttribute('data-comment-id');
  commentFormContent.value = `${commentUsername}, `;
  commentFormParentInput.value = commentMessageId;
}
async function createComment(event) {
    event.preventDefault();
    commentFormSubmit.disabled = true;
    commentFormSubmit.innerText = "Ожидаем ответа сервера";
    let csrftoken = getCookie('csrftoken');
    try {
        const response = await fetch(`/post/${commentPostId}/comments/create/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: new FormData(commentForm),
        });
        const comment = await response.json();

        let commentTemplate = `<ul id="comment-thread-${comment.id}">
                                <li class="comment">
                                    <div class="comment-block">
                                        <img src="${comment.avatar}" style="width: 40px;height: 40px;object-fit: cover;" alt="${comment.author}"/>
                                        <div class="comment-content">
                                            <div class="comment-author-block">
                                                <a class="comment-author" href="${comment.get_absolute_url}">${comment.author}</a>
                                                <time>${comment.time_create}</time>
                                            </div>
                                            <p class="comment-text">
                                                ${comment.content}
                                            </p>
                                        </div>
                                    </div>
                                    <div class="comment-actions">
                                        <a class="btn-reply comment-action" href="#commentForm" data-comment-id="${comment.id}" data-comment-username="${comment.author}">Ответить</a>
                                        <button type="button" class="comment-action comment-delete" data-comment-id="${comment.id}" data-comment-username="${comment.author}">Удалить</button>
                                    </div>
                                </li>
                            </ul>`;
        if (comment.is_child) {
            document.querySelector(`#comment-thread-${comment.parent_id}`).insertAdjacentHTML("beforeend", commentTemplate);
        }
        else {
            document.querySelector('.nested-comments').insertAdjacentHTML("beforeend", commentTemplate)
        }
        commentForm.reset()
        commentFormSubmit.disabled = false;
        commentFormSubmit.innerText = "Добавить комментарий";
        commentFormParentInput.value = null;
        replyUser();
        listenDeleteBtn();
    }
    catch (error) {
        console.log(error)
    }
}


function deleteComment() {
    console.log('deleteComment');
    const csrftoken = getCookie('csrftoken');
    const commentMessageId = this.getAttribute('data-comment-id');
    fetch(`/post/${commentMessageId}/comments/delete/`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": csrftoken,
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then(data => {
        const comment = document.getElementById("comment-thread-" + commentMessageId);
        comment.remove();
    })
    .catch(error => console.error(error));
}

function listenDeleteBtn() {
    document.querySelectorAll('.comment-delete').forEach(e => {
        e.addEventListener('click', deleteComment);
      });
}


