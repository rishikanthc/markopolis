export function preprocessImages(baseUrl) {
  const imageExtensions = ['png', 'jpg', 'jpeg', 'webp', 'svg'];
  const extensionPattern = imageExtensions.join('|');
  const regex = new RegExp(`(.*?\\.(${extensionPattern}))`, 'i');

  return ({ content, filename }) => {
    if (filename.endsWith('.svelte')) {
      return {
        code: content.replace(/<img([^>]*)src="([^"]+)"([^>]*)>/g, (match, before, src, after) => {
          if (regex.test(src)) {
            // Remove leading slash if present
            const cleanSrc = src.startsWith('/') ? src.slice(1) : src;
            return `<img${before}src="${baseUrl}/${cleanSrc}"${after}>`;
          }
          return match;
        })
      };
    }
  };
}
