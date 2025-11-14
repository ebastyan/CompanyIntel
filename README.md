# 🏢 Romanian Companies Directory

A comprehensive Next.js application for exploring Romanian company profiles, similar to listafirme.ro, featuring financial data visualization, search functionality, and business analytics.

![Next.js](https://img.shields.io/badge/Next.js-14.0+-black?style=flat&logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=flat&logo=typescript)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue?style=flat&logo=postgresql)
![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.3+-blue?style=flat&logo=tailwindcss)
![Vercel](https://img.shields.io/badge/Vercel-Ready-black?style=flat&logo=vercel)

## 🌟 Features

### 🏪 Company Profiles
- **Detailed company information** with CIF, registration numbers, and status
- **Financial data visualization** with interactive charts (revenue, profit, employees)
- **Multi-year financial trends** and growth analysis
- **Performance indicators** and business metrics
- **Contact information** with maps integration
- **CAEN activity codes** and business descriptions

### 🔍 Advanced Search
- **Full-text search** across company names, CIF numbers, and activities
- **Advanced filters** by county, business sector, revenue, and employee count
- **Real-time search** with debounced input
- **Sorting options** by revenue, profit, employees, and name
- **Pagination** with responsive design

### 📊 Business Analytics
- **Company rankings** by revenue, profit, and growth
- **Sector analysis** with industry breakdowns
- **Regional statistics** by county performance
- **Market trends** and comparative analysis

### 🌐 International Support
- **Multi-language support** (Romanian/English)
- **Responsive design** optimized for mobile, tablet, and desktop
- **SEO optimized** with structured data and meta tags
- **Performance optimized** with caching and CDN

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** and npm
- **PostgreSQL database** (Neon DB recommended)
- **Git** for version control

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/your-username/romanian-companies-app.git
cd romanian-companies-app

# Install dependencies
npm install
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env.local

# Edit with your database credentials
nano .env.local
```

**Required environment variables:**

```env
DATABASE_URL="postgresql://username:password@your-neon-host/database?sslmode=require"
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key"
```

### 3. Database Setup

```bash
# Run database migrations
npm run db:migrate

# Seed with your data (optional)
npm run db:seed
```

### 4. Development Server

```bash
# Start development server
npm run dev

# Open browser to http://localhost:3000
```

## 🗄️ Database Schema

The application uses a normalized PostgreSQL schema optimized for Romanian business data:

### Core Tables

- **`companies`** - Basic company information (CIF, name, status)
- **`company_financials`** - Annual financial data (revenue, profit, employees)
- **`company_addresses`** - Company locations with geolocation
- **`company_contacts`** - Email, phone, website information
- **`caen_codes`** - Romanian business activity classifications
- **`company_caen`** - Many-to-many relationship for company activities

### Features

- **UUID primary keys** for performance
- **Full-text search** with Romanian language support
- **Composite indexes** for complex queries
- **Views and functions** for business logic
- **Row-level security** ready for multi-tenant setups

## 📁 Project Structure

```
romanian-companies-app/
├── src/
│   ├── app/
│   │   ├── [locale]/              # Internationalized routes
│   │   │   ├── company/[cif]/     # Company profile pages
│   │   │   └── page.tsx           # Homepage
│   │   ├── api/                   # API routes
│   │   │   ├── companies/         # Company data endpoints
│   │   │   ├── search/            # Search functionality
│   │   │   ├── rankings/          # Performance rankings
│   │   │   └── stats/             # Statistics and analytics
│   │   └── globals.css            # Global styles
│   ├── components/
│   │   ├── charts/                # Financial chart components
│   │   ├── company/               # Company-related components
│   │   ├── layout/                # Header, footer, navigation
│   │   └── ui/                    # Reusable UI components
│   ├── lib/
│   │   └── database.ts            # Database connection and queries
│   ├── messages/                  # i18n translations
│   ├── types/                     # TypeScript definitions
│   └── utils/                     # Utility functions
├── scripts/
│   ├── migrate.js                 # Database migration script
│   ├── seed.js                    # Data seeding script
│   └── neon-schema.sql            # PostgreSQL schema
├── public/                        # Static assets
└── docs/                          # Additional documentation
```

## 🛠️ Development

### Available Scripts

```bash
# Development
npm run dev              # Start development server
npm run build            # Build for production
npm run start            # Start production server
npm run lint             # Run ESLint

# Database
npm run db:migrate       # Run database migrations
npm run db:seed          # Populate with data

# Type checking
npm run type-check       # Run TypeScript compiler
```

### Code Quality

- **TypeScript** for type safety
- **ESLint** and **Prettier** for code formatting
- **Husky** for pre-commit hooks
- **Conventional commits** for git history

### Testing

```bash
npm run test             # Run unit tests
npm run test:e2e         # Run end-to-end tests
npm run test:coverage    # Generate coverage report
```

## 🌐 Deployment

### Vercel (Recommended)

The application is optimized for Vercel deployment:

1. **Connect to GitHub**
   ```bash
   # Push to GitHub repository
   git remote add origin https://github.com/your-username/romanian-companies-app.git
   git push -u origin main
   ```

2. **Deploy to Vercel**
   - Visit [vercel.com](https://vercel.com) and import your repository
   - Add environment variables in Vercel dashboard
   - Deploy automatically on every push

3. **Set up Neon Database**
   - Create database at [neon.tech](https://neon.tech)
   - Copy connection string to `DATABASE_URL`
   - Run migrations: `npm run db:migrate`

### Environment Variables for Production

```env
DATABASE_URL="postgresql://..."
NEXTAUTH_URL="https://your-domain.vercel.app"
NEXTAUTH_SECRET="secure-random-string"
NODE_ENV="production"
```

### Alternative Deployment Platforms

- **Railway**: PostgreSQL + Next.js hosting
- **PlanetScale + Netlify**: MySQL variant
- **AWS**: EC2 + RDS deployment
- **DigitalOcean**: App Platform + Managed Database

## 📊 Data Import

### From Excel Files

The application can import data from Excel files:

```bash
# Place Excel files in project root
# Run seed script
npm run db:seed
```

**Expected Excel columns:**
- `CIF` - Company tax ID
- `Denumire` - Company name
- `Judet` - County
- `Localitate` - City
- `An` - Financial year
- `Cifra_afaceri` - Revenue
- `Profit` - Net profit
- `Salariati` - Employee count

### From CSV Files

```bash
# Convert CSV to Excel or modify seed script
node scripts/import-csv.js your-data.csv
```

### From API Sources

```bash
# Set up data sync from external APIs
node scripts/sync-external-data.js
```

## 🔧 Configuration

### Tailwind CSS

Customize the design system in `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: { /* Your brand colors */ },
        secondary: { /* Secondary palette */ }
      }
    }
  }
}
```

### Internationalization

Add new languages in `src/messages/`:

```bash
# Add new language file
cp src/messages/ro.json src/messages/fr.json
```

Update `middleware.ts`:
```typescript
const locales = ['ro', 'en', 'fr'];
```

### Database Optimization

For large datasets (100K+ companies):

1. **Add database indexes**
```sql
CREATE INDEX CONCURRENTLY idx_companies_search
ON companies USING gin(to_tsvector('romanian', company_name));
```

2. **Enable connection pooling**
```typescript
const pool = new Pool({
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});
```

3. **Implement Redis caching**
```bash
npm install redis
```

## 📈 Performance

### Optimization Features

- **Image optimization** with Next.js Image component
- **Code splitting** with dynamic imports
- **API caching** with stale-while-revalidate
- **Database query optimization** with indexes
- **CDN integration** for static assets

### Monitoring

- **Vercel Analytics** for web vitals
- **Sentry** for error tracking
- **Database monitoring** with Neon metrics

### Load Testing

```bash
# Install artillery for load testing
npm install -g artillery

# Run load tests
artillery quick --count 100 --num 10 http://localhost:3000
```

## 🔒 Security

### Security Features

- **SQL injection protection** with parameterized queries
- **XSS protection** with Content Security Policy
- **CSRF protection** with Next.js built-in features
- **Rate limiting** on API endpoints
- **Input validation** with TypeScript and Zod

### Security Headers

Configured in `next.config.js`:
```javascript
const securityHeaders = [
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on'
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload'
  }
];
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with tests
4. **Run quality checks**: `npm run lint && npm run type-check`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Guidelines

- Follow **TypeScript best practices**
- Write **comprehensive tests**
- Use **semantic commit messages**
- Document **API changes**
- Ensure **accessibility compliance**

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Romanian Ministry of Finance** for public company data
- **Neon** for PostgreSQL hosting
- **Vercel** for Next.js deployment platform
- **Tailwind CSS** for the design system
- **Chart.js** for data visualizations
- **Next-intl** for internationalization
- **React Hook Form** for form handling

## 📞 Support

### Getting Help

- 📖 **Documentation**: [docs/](docs/)
- 💬 **Discussions**: GitHub Discussions
- 🐛 **Bug Reports**: GitHub Issues
- 📧 **Email**: contact@your-domain.com

### Roadmap

See our [Project Roadmap](https://github.com/your-username/romanian-companies-app/projects/1) for upcoming features:

- [ ] Advanced analytics dashboard
- [ ] Company comparison tools
- [ ] Export to PDF/Excel functionality
- [ ] Real-time data synchronization
- [ ] Mobile application
- [ ] API access for developers

---

**Built with ❤️ for the Romanian business community**

*Last updated: November 2024*