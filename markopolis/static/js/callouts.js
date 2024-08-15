document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.callout.collapsible .callout-title').forEach(title => {
        title.addEventListener('click', function() {
            const callout = this.closest('.callout');
            callout.classList.toggle('expanded');
        });
    });
});
