import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { 
  Search, 
  Bell, 
  FileText, 
  BarChart3, 
  Globe, 
  CheckCircle, 
  ArrowRight, 
  Users, 
  Building, 
  Zap,
  Mail,
  Star,
  TrendingUp,
  Shield,
  Clock
} from 'lucide-react'
import './App.css'

function App() {
  const [language, setLanguage] = useState('et') // Default to Estonian
  const [email, setEmail] = useState('')

  const content = {
    et: {
      nav: {
        features: 'Funktsioonid',
        pricing: 'Hinnad',
        about: 'Meist',
        login: 'Logi sisse'
      },
      hero: {
        title: 'Eesti Riigihanked',
        subtitle: 'AI-põhine Platvorm',
        description: 'Avasta, analüüsi ja osale Eesti riigihangetes nutika tehisintellekti toel. Automatiseeri hankedokumentide täitmine ja saa kohandatud teateid.',
        cta: 'Alusta Tasuta',
        demo: 'Vaata Demot'
      },
      stats: {
        procurements: 'Hankeid',
        companies: 'Ettevõtet',
        value: 'Koguväärtus',
        success: 'Edukus'
      },
      features: {
        title: 'Miks Valida Hange AI?',
        subtitle: 'Kõik vajalik riigihangetes osalemiseks ühes kohas',
        search: {
          title: 'Nutikas Otsing',
          description: 'AI-põhine otsing leiab sulle sobivaimad hanked automaatselt'
        },
        notifications: {
          title: 'Kohandatud Teatised',
          description: 'Saa e-kirja teel teateid uutest hangetest, mis vastavad sinu kriteeriumitele'
        },
        documents: {
          title: 'Automaatne Dokumentide Täitmine',
          description: 'AI täidab hankedokumendid automaatselt sinu andmete põhjal'
        },
        analytics: {
          title: 'Analüütika ja Aruanded',
          description: 'Jälgi oma edusamme ja hanketuru trende'
        }
      },
      howItWorks: {
        title: 'Kuidas See Töötab',
        step1: {
          title: 'Registreeru',
          description: 'Loo konto ja määra oma huvialad'
        },
        step2: {
          title: 'Saa Teateid',
          description: 'Saad automaatselt teateid sobivate hangete kohta'
        },
        step3: {
          title: 'Osale Hangetel',
          description: 'Kasuta AI-d dokumentide täitmiseks ja pakkumuste esitamiseks'
        }
      },
      testimonials: {
        title: 'Mida Meie Kliendid Ütlevad',
        testimonial1: {
          text: 'Hange AI on revolutsiooniliselt muutnud meie osalust riigihangetes. Säästame aega ja leiame rohkem sobivaid võimalusi.',
          author: 'Mari Kask',
          company: 'TechSolutions OÜ'
        },
        testimonial2: {
          text: 'Automaatne dokumentide täitmine on meie jaoks mängumuutja. Varem kulus sellele tunde, nüüd minuteid.',
          author: 'Peeter Tamm',
          company: 'BuildCorp AS'
        }
      },
      cta: {
        title: 'Alusta Täna',
        description: 'Liitu tuhandete ettevõtetega, kes kasutavad Hange AI-d',
        button: 'Registreeru Tasuta'
      },
      footer: {
        company: 'Ettevõte',
        product: 'Toode',
        support: 'Tugi',
        legal: 'Õiguslik'
      }
    },
    en: {
      nav: {
        features: 'Features',
        pricing: 'Pricing',
        about: 'About',
        login: 'Sign In'
      },
      hero: {
        title: 'Estonian Public',
        subtitle: 'Procurement AI Platform',
        description: 'Discover, analyze, and participate in Estonian public procurements with intelligent AI assistance. Automate document filling and receive personalized notifications.',
        cta: 'Start Free',
        demo: 'Watch Demo'
      },
      stats: {
        procurements: 'Procurements',
        companies: 'Companies',
        value: 'Total Value',
        success: 'Success Rate'
      },
      features: {
        title: 'Why Choose Hange AI?',
        subtitle: 'Everything you need for public procurement participation in one place',
        search: {
          title: 'Smart Search',
          description: 'AI-powered search automatically finds the most suitable procurements for you'
        },
        notifications: {
          title: 'Custom Notifications',
          description: 'Receive email alerts for new procurements matching your criteria'
        },
        documents: {
          title: 'Automatic Document Filling',
          description: 'AI automatically fills procurement documents based on your data'
        },
        analytics: {
          title: 'Analytics & Reports',
          description: 'Track your progress and procurement market trends'
        }
      },
      howItWorks: {
        title: 'How It Works',
        step1: {
          title: 'Sign Up',
          description: 'Create an account and set your interests'
        },
        step2: {
          title: 'Get Notified',
          description: 'Automatically receive alerts about suitable procurements'
        },
        step3: {
          title: 'Participate',
          description: 'Use AI to fill documents and submit proposals'
        }
      },
      testimonials: {
        title: 'What Our Clients Say',
        testimonial1: {
          text: 'Hange AI has revolutionized our participation in public procurements. We save time and find more suitable opportunities.',
          author: 'Mari Kask',
          company: 'TechSolutions OÜ'
        },
        testimonial2: {
          text: 'Automatic document filling is a game-changer for us. What used to take hours now takes minutes.',
          author: 'Peeter Tamm',
          company: 'BuildCorp AS'
        }
      },
      cta: {
        title: 'Start Today',
        description: 'Join thousands of companies using Hange AI',
        button: 'Sign Up Free'
      },
      footer: {
        company: 'Company',
        product: 'Product',
        support: 'Support',
        legal: 'Legal'
      }
    }
  }

  const t = content[language]

  const handleEmailSubmit = (e) => {
    e.preventDefault()
    // Redirect to Streamlit app with email parameter
    window.open(`https://hange-ai.streamlit.app/?email=${encodeURIComponent(email)}`, '_blank')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Building className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">Hange AI</span>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">{t.nav.features}</a>
              <a href="#pricing" className="text-gray-600 hover:text-gray-900 transition-colors">{t.nav.pricing}</a>
              <a href="#about" className="text-gray-600 hover:text-gray-900 transition-colors">{t.nav.about}</a>
              <Button variant="outline" size="sm">{t.nav.login}</Button>
            </div>

            <div className="flex items-center space-x-2">
              <Button
                variant={language === 'et' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setLanguage('et')}
                className="text-xs"
              >
                EST
              </Button>
              <Button
                variant={language === 'en' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setLanguage('en')}
                className="text-xs"
              >
                ENG
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <Badge className="mb-4 bg-blue-100 text-blue-800 hover:bg-blue-200">
              <Zap className="w-3 h-3 mr-1" />
              AI-Powered Platform
            </Badge>
            
            <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6">
              {t.hero.title}
              <br />
              <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                {t.hero.subtitle}
              </span>
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              {t.hero.description}
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <Button size="lg" className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700">
                {t.hero.cta}
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
              <Button variant="outline" size="lg">
                {t.hero.demo}
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900">10,000+</div>
                <div className="text-gray-600">{t.stats.procurements}</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900">2,500+</div>
                <div className="text-gray-600">{t.stats.companies}</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900">€2.7B</div>
                <div className="text-gray-600">{t.stats.value}</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900">94%</div>
                <div className="text-gray-600">{t.stats.success}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              {t.features.title}
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              {t.features.subtitle}
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <Search className="w-6 h-6 text-blue-600" />
                </div>
                <CardTitle>{t.features.search.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>{t.features.search.description}</CardDescription>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <Bell className="w-6 h-6 text-green-600" />
                </div>
                <CardTitle>{t.features.notifications.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>{t.features.notifications.description}</CardDescription>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                  <FileText className="w-6 h-6 text-purple-600" />
                </div>
                <CardTitle>{t.features.documents.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>{t.features.documents.description}</CardDescription>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
                  <BarChart3 className="w-6 h-6 text-orange-600" />
                </div>
                <CardTitle>{t.features.analytics.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>{t.features.analytics.description}</CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              {t.howItWorks.title}
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <Users className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">{t.howItWorks.step1.title}</h3>
              <p className="text-gray-600">{t.howItWorks.step1.description}</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <Bell className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">{t.howItWorks.step2.title}</h3>
              <p className="text-gray-600">{t.howItWorks.step2.description}</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">{t.howItWorks.step3.title}</h3>
              <p className="text-gray-600">{t.howItWorks.step3.description}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              {t.testimonials.title}
            </h2>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <Card className="border-0 shadow-lg">
              <CardContent className="p-8">
                <div className="flex mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-600 mb-6 italic">"{t.testimonials.testimonial1.text}"</p>
                <div>
                  <div className="font-semibold text-gray-900">{t.testimonials.testimonial1.author}</div>
                  <div className="text-gray-500">{t.testimonials.testimonial1.company}</div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg">
              <CardContent className="p-8">
                <div className="flex mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-600 mb-6 italic">"{t.testimonials.testimonial2.text}"</p>
                <div>
                  <div className="font-semibold text-gray-900">{t.testimonials.testimonial2.author}</div>
                  <div className="text-gray-500">{t.testimonials.testimonial2.company}</div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl lg:text-4xl font-bold text-white mb-4">
            {t.cta.title}
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            {t.cta.description}
          </p>
          
          <form onSubmit={handleEmailSubmit} className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
            <Input
              type="email"
              placeholder="your.email@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-white/10 border-white/20 text-white placeholder:text-white/60"
              required
            />
            <Button type="submit" variant="secondary" className="bg-white text-blue-600 hover:bg-gray-100">
              {t.cta.button}
            </Button>
          </form>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                  <Building className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">Hange AI</span>
              </div>
              <p className="text-gray-400">
                {language === 'et' 
                  ? 'Eesti riigihangete AI-platvorm ettevõtetele'
                  : 'Estonian procurement AI platform for businesses'
                }
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-4">{t.footer.product}</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">{t.nav.features}</a></li>
                <li><a href="#" className="hover:text-white transition-colors">{t.nav.pricing}</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">{t.footer.company}</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">{t.nav.about}</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">{t.footer.support}</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Status</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 Hange AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App

