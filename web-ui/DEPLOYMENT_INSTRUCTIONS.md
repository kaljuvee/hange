# Hange AI Landing Page - Deployment Instructions

## Overview

This is a professional, bilingual (Estonian/English) landing page for the Hange AI procurement platform, built with React, Tailwind CSS, and shadcn/ui components.

## Features

✅ **Bilingual Support**: Estonian (default) and English versions
✅ **Modern Design**: Inspired by stotles.com with professional styling
✅ **Responsive Layout**: Works on desktop and mobile devices
✅ **Interactive Elements**: Language switching, email signup, smooth scrolling
✅ **Email Integration**: Redirects to Streamlit app with email parameter
✅ **Professional Components**: Cards, badges, buttons, testimonials
✅ **Gradient Design**: Modern blue/indigo gradient theme

## Project Structure

```
ui/hange-landing/
├── public/
├── src/
│   ├── components/ui/     # shadcn/ui components
│   ├── App.jsx           # Main landing page component
│   ├── App.css           # Tailwind CSS styles
│   └── main.jsx          # Entry point
├── index.html            # HTML template
├── package.json          # Dependencies
└── vite.config.js        # Vite configuration
```

## Local Development

1. **Navigate to project directory:**
   ```bash
   cd ui/hange-landing
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev --host
   ```

4. **Open in browser:**
   ```
   http://localhost:5173
   ```

## Deployment Options

### 1. Netlify Deployment

**Steps:**
1. Build the project:
   ```bash
   npm run build
   ```

2. Upload the `dist/` folder to Netlify:
   - Go to [netlify.com](https://netlify.com)
   - Drag and drop the `dist` folder
   - Or connect your GitHub repository

**Configuration:**
- Build command: `npm run build`
- Publish directory: `dist`
- Node version: 18 or higher

### 2. Vercel Deployment

**Steps:**
1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy:
   ```bash
   vercel --prod
   ```

**Configuration:**
- Framework: React
- Build command: `npm run build`
- Output directory: `dist`

### 3. Render Deployment

**Steps:**
1. Connect your GitHub repository to [render.com](https://render.com)

2. Create a new Static Site with these settings:
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Node version: 18

### 4. GitHub Pages Deployment

**Steps:**
1. Install gh-pages:
   ```bash
   npm install --save-dev gh-pages
   ```

2. Add to package.json:
   ```json
   {
     "homepage": "https://yourusername.github.io/hange",
     "scripts": {
       "predeploy": "npm run build",
       "deploy": "gh-pages -d dist"
     }
   }
   ```

3. Deploy:
   ```bash
   npm run deploy
   ```

## Environment Configuration

### Production URLs
Update the Streamlit app URL in `App.jsx` if needed:
```javascript
window.open(`https://your-streamlit-app.com/?email=${encodeURIComponent(email)}`, '_blank')
```

### Custom Domain
For custom domains, update:
1. DNS settings to point to your hosting provider
2. SSL certificate configuration
3. Any hardcoded URLs in the application

## Performance Optimization

### Already Implemented:
- ✅ Vite bundler for fast builds
- ✅ Tree shaking for smaller bundle size
- ✅ CSS optimization with Tailwind
- ✅ Component lazy loading ready
- ✅ Responsive images and icons

### Additional Optimizations:
1. **Image Optimization**: Add optimized images to `src/assets/`
2. **CDN**: Use a CDN for static assets
3. **Caching**: Configure proper cache headers
4. **Analytics**: Add Google Analytics or similar

## SEO Configuration

### Meta Tags (add to index.html):
```html
<meta name="description" content="Estonian Public Procurement AI Platform - Discover, analyze, and participate in Estonian public procurements with intelligent AI assistance.">
<meta name="keywords" content="Estonia, procurement, AI, public tenders, riigihangked">
<meta property="og:title" content="Hange AI - Estonian Procurement Intelligence Platform">
<meta property="og:description" content="AI-powered platform for Estonian public procurement participation">
<meta property="og:image" content="/og-image.jpg">
<meta property="og:url" content="https://your-domain.com">
```

### Sitemap and Robots.txt:
Add to `public/` directory for better SEO.

## Monitoring and Analytics

### Recommended Tools:
1. **Google Analytics**: Track user behavior
2. **Hotjar**: User session recordings
3. **Sentry**: Error monitoring
4. **Lighthouse**: Performance monitoring

## Maintenance

### Regular Updates:
1. **Dependencies**: Update npm packages monthly
2. **Security**: Monitor for security vulnerabilities
3. **Performance**: Regular Lighthouse audits
4. **Content**: Update testimonials and statistics

### Backup Strategy:
1. **Code**: GitHub repository
2. **Deployment**: Multiple hosting providers
3. **Assets**: Cloud storage backup

## Integration with Streamlit App

### Current Integration:
- Email parameter passing: `?email=user@example.com`
- Opens in new tab for seamless user experience

### Future Enhancements:
1. **Single Sign-On**: Implement OAuth integration
2. **API Integration**: Direct API calls to backend
3. **Real-time Data**: Live procurement statistics
4. **User Dashboard**: Embedded Streamlit components

## Support and Documentation

### Resources:
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [shadcn/ui Components](https://ui.shadcn.com)
- [Vite Documentation](https://vitejs.dev)

### Contact:
For technical support or questions about deployment, contact the development team.

## License

This project is proprietary software for Hange AI platform.

---

**Last Updated**: September 3, 2025
**Version**: 1.0.0
**Status**: Production Ready ✅

