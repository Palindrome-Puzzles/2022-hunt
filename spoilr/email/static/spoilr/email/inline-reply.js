const replyForm = document.querySelector('.email-reply-form');
if (replyForm) {
  const bodyTextarea = replyForm.querySelector('textarea');
  const messageIdField = replyForm.querySelector('[name=id]');
  const cancelButton = replyForm.querySelector('button');

  replyForm.classList.toggle('hidden', true);
  for (const replyButton of document.querySelectorAll('.email-reply-button')) {
    const messageId = replyButton.dataset.messageId;
    if (!messageId) throw new Error('Missing reply button message ID');

    replyButton.addEventListener('click', () => {
      const actionsContainer = replyButton.closest('.actions');
      actionsContainer.parentNode.insertBefore(replyForm, actionsContainer.nextElementSibling);

      replyForm.classList.toggle('hidden', false);
      messageIdField.value = messageId;
      bodyTextarea.value = '';
      bodyTextarea.focus();
    });
  }

  cancelButton.addEventListener('click', () => {
    replyForm.classList.toggle('hidden', true);
    bodyTextarea.value = '';
    messageIdField.value = '';
  })
}
