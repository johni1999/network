document.addEventListener('DOMContentLoaded', function() {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function attachEditListeners() {
        document.querySelectorAll('.edit-button').forEach(button => {
            button.addEventListener('click', function () {
                const postId = this.getAttribute('data-post-id');
                const postContentElement = document.getElementById(`post-content-${postId}`);
                
                if (!postContentElement) {
                    console.error(`Post content element not found for post ID: ${postId}`);
                    return;
                }

                const originalContent = postContentElement.textContent;

                // Replace the post content with a textarea
                const textarea = document.createElement('textarea');
                textarea.className = 'form-control';
                textarea.value = originalContent;
                postContentElement.replaceWith(textarea);

                // Create a "Save" button
                const saveButton = document.createElement('button');
                saveButton.className = 'btn btn-sm btn-primary mt-2';
                saveButton.textContent = 'Save';
                this.replaceWith(saveButton);

                // Handle saving the edited post
                saveButton.addEventListener('click', function () {
                    const updatedContent = textarea.value;

                    // Send the updated content to the server via AJAX
                    fetch(`/edit_post/${postId}/`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({ content: updatedContent })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Replace the textarea with the updated content
                            const updatedContentElement = document.createElement('p');
                            updatedContentElement.className = 'card-text';
                            updatedContentElement.id = `post-content-${postId}`;
                            updatedContentElement.textContent = updatedContent;
                            textarea.replaceWith(updatedContentElement);

                            // Replace the "Save" button with the "Edit" button
                            const editButton = document.createElement('button');
                            editButton.className = 'btn btn-sm btn-secondary edit-button';
                            editButton.textContent = 'Edit';
                            editButton.setAttribute('data-post-id', postId);
                            saveButton.replaceWith(editButton);

                            // Reattach the event listener to the new "Edit" button
                            attachEditListeners();
                        } else {
                            console.error('Failed to update post:', data.error);
                        }
                    })
                    .catch(error => console.error('Error:', error));
                });
            });
        });
    }

    // Attach event listeners to all edit buttons initially
    attachEditListeners();

    // Attach event listeners to like buttons
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', function () {
            const postId = this.getAttribute('data-post-id');
            const likeCount = document.getElementById(`like-count-${postId}`);
            const likeButton = this;

            fetch(`/toggle_like/${postId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.liked) {
                    likeButton.textContent = 'Unlike 👎';
                } else {
                    likeButton.textContent = 'Like 👍';
                }
                likeCount.textContent = `Likes: ${data.like_count}`;
            })
            .catch(error => console.error('Error:', error));
        });
    });
});
