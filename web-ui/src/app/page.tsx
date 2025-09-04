'use client'

import { useState } from 'react'
import { 
  ChevronRight, 
  Search, 
  FileText, 
  Mail, 
  BarChart3, 
  Star,
  ArrowRight,
  Award,
  Zap,
  Shield,
  Clock
} from 'lucide-react'

export default function Home() {
  const [language, setLanguage] = useState<'et' | 'en'>('et')

  const content = {
    et: {
      title: 'Hange AI',
      subtitle: 'Eesti Riigihanke Intelligentsuse Platvorm',
      description: 'AI-põhine riigihangete otsing intelligentsete ülevaadete ja automatiseeritud dokumenditöötlusega',
      hero: {
        badge: 'Uus! AI-põhine dokumenditöötlus',
        cta: 'Alusta tasuta',
        demo: 'Vaata demo',
        trusted: 'Usaldavad 500+ ettevõtet'
      },
      features: {
        title: 'Miks valida Hange AI?',
        subtitle: 'Kõik, mida vajate riigihangetes osalemiseks ühes kohas',
        items: [
          {
            icon: Search,
            title: 'Intelligentne otsing',
            description: 'AI-põhine riigihangete avastamine reaalajas RSS-voo abil. Leia sobivad hanked automaatselt.'
          },
          {
            icon: FileText,
            title: 'Dokumenditöötlus',
            description: 'OpenAI-põhine vormiväljade ekstrakteerimine 90% täpsusega. Säästke tunde dokumentide täitmisel.'
          },
          {
            icon: Mail,
            title: 'E-posti teavitused',
            description: 'Isikupärastatud hoiatused sektoripõhise filtreerimisega. Ärge jätke ühtegi võimalust vahele.'
          },
          {
            icon: BarChart3,
            title: 'Analüütika ja ülevaated',
            description: 'Interaktiivsed diagrammid ja riigihangete statistika. Tehke andmepõhiseid otsuseid.'
          },
          {
            icon: Zap,
            title: '10x kiirem töötlemine',
            description: 'Intelligentne vahemällu salvestamine ja optimeeritud töövood kiirendavad protsesse.'
          },
          {
            icon: Shield,
            title: 'Turvaline ja usaldusväärne',
            description: 'Enterprise-tasemel turvalisus ja 99.9% töökindlus. Teie andmed on kaitstud.'
          }
        ]
      },
      stats: [
        { number: '712+', label: 'Aktiivset hanget', icon: FileText },
        { number: '90%', label: 'AI täpsus', icon: Award },
        { number: '10x', label: 'Kiirem töötlemine', icon: Zap },
        { number: '24/7', label: 'Reaalajas andmed', icon: Clock }
      ],
      testimonials: [
        {
          name: 'Mari Kask',
          company: 'TechSolutions OÜ',
          role: 'Tegevjuht',
          text: 'Hange AI on revolutsioneerinud meie osalemist riigihangetes. Säästame aega ja leiame rohkem sobivaid võimalusi. Meie edukus on kasvanud 40%.',
          rating: 5
        },
        {
          name: 'Peeter Tamm',
          company: 'BuildCorp AS',
          role: 'Projektijuht',
          text: 'Automaatne dokumenditäitmine on meie jaoks mängumuutja. See, mis varem võttis tunde, võtab nüüd minuteid. Soovitan kõigile!',
          rating: 5
        }
      ],
      cta: {
        title: 'Valmis alustama?',
        subtitle: 'Liitu tuhandete ettevõtetega, kes kasutavad Hange AI-d riigihangetes edukaks osalemiseks',
        button: 'Registreeru tasuta',
        placeholder: 'sinu.email@näide.com',
        guarantee: '14-päevane raha tagasi garantii'
      }
    },
    en: {
      title: 'Hange AI',
      subtitle: 'Estonian Procurement Intelligence Platform',
      description: 'AI-powered procurement search with intelligent insights and automated document processing',
      hero: {
        badge: 'New! AI-powered document processing',
        cta: 'Start Free',
        demo: 'Watch Demo',
        trusted: 'Trusted by 500+ companies'
      },
      features: {
        title: 'Why Choose Hange AI?',
        subtitle: 'Everything you need for procurement participation in one place',
        items: [
          {
            icon: Search,
            title: 'Intelligent Search',
            description: 'AI-powered procurement discovery with real-time RSS feed. Find relevant tenders automatically.'
          },
          {
            icon: FileText,
            title: 'Document Processing',
            description: 'OpenAI-powered form field extraction with 90% accuracy. Save hours on document completion.'
          },
          {
            icon: Mail,
            title: 'Email Notifications',
            description: 'Personalized alerts with sector-based filtering. Never miss an opportunity again.'
          },
          {
            icon: BarChart3,
            title: 'Analytics & Insights',
            description: 'Interactive charts and procurement statistics. Make data-driven decisions.'
          },
          {
            icon: Zap,
            title: '10x Faster Processing',
            description: 'Intelligent caching and optimized workflows accelerate your processes.'
          },
          {
            icon: Shield,
            title: 'Secure & Reliable',
            description: 'Enterprise-grade security and 99.9% uptime. Your data is protected.'
          }
        ]
      },
      stats: [
        { number: '712+', label: 'Active Procurements', icon: FileText },
        { number: '90%', label: 'AI Accuracy', icon: Award },
        { number: '10x', label: 'Faster Processing', icon: Zap },
        { number: '24/7', label: 'Real-time Data', icon: Clock }
      ],
      testimonials: [
        {
          name: 'Mari Kask',
          company: 'TechSolutions OÜ',
          role: 'CEO',
          text: 'Hange AI has revolutionized our participation in public procurements. We save time and find more suitable opportunities. Our success rate increased by 40%.',
          rating: 5
        },
        {
          name: 'Peeter Tamm',
          company: 'BuildCorp AS',
          role: 'Project Manager',
          text: 'Automatic document filling is a game-changer for us. What used to take hours now takes minutes. Highly recommend to everyone!',
          rating: 5
        }
      ],
      cta: {
        title: 'Ready to Get Started?',
        subtitle: 'Join thousands of companies using Hange AI for successful procurement participation',
        button: 'Sign Up Free',
        placeholder: 'your.email@example.com',
        guarantee: '14-day money-back guarantee'
      }
    }
  }

  const t = content[language]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-md border-b border-blue-100 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-lg">H</span>
              </div>
              <div>
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  {t.title}
                </span>
                <div className="text-xs text-gray-500 -mt-1">AI Platform</div>
              </div>
            </div>
            
            <nav className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors font-medium">
                {language === 'et' ? 'Funktsioonid' : 'Features'}
              </a>
              <a href="#testimonials" className="text-gray-600 hover:text-blue-600 transition-colors font-medium">
                {language === 'et' ? 'Arvustused' : 'Testimonials'}
              </a>
              <button 
                onClick={() => window.open('https://hange.onrender.com/', '_blank')}
                className="px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium"
              >
                {language === 'et' ? 'Logi sisse' : 'Sign In'}
              </button>
            </nav>

            <div className="flex items-center space-x-3">
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setLanguage('et')}
                  className={`px-3 py-1 rounded-md text-sm font-medium transition-all ${
                    language === 'et' 
                      ? 'bg-white text-blue-600 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  EST
                </button>
                <button
                  onClick={() => setLanguage('en')}
                  className={`px-3 py-1 rounded-md text-sm font-medium transition-all ${
                    language === 'en' 
                      ? 'bg-white text-blue-600 shadow-sm' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  ENG
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 to-indigo-600/5"></div>
        <div className="max-w-7xl mx-auto text-center relative">
          <div className="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium mb-8">
            <Star className="w-4 h-4 mr-2" />
            {t.hero.badge}
          </div>
          
          <h1 className="text-6xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
            <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
              {t.title}
            </span>
          </h1>
          <h2 className="text-3xl md:text-4xl text-gray-700 mb-8 font-light">{t.subtitle}</h2>
          <p className="text-xl text-gray-600 mb-12 max-w-4xl mx-auto leading-relaxed">{t.description}</p>
          
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
            {t.stats.map((stat, index) => (
              <div key={index} className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 border border-blue-100 shadow-lg hover:shadow-xl transition-shadow">
                <stat.icon className="w-8 h-8 text-blue-600 mx-auto mb-4" />
                <div className="text-4xl font-bold text-blue-600 mb-2">{stat.number}</div>
                <div className="text-gray-600 font-medium">{stat.label}</div>
              </div>
            ))}
          </div>

          {/* CTA */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-10 border border-blue-100 shadow-xl max-w-2xl mx-auto">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">{t.cta.title}</h3>
            <p className="text-gray-600 mb-8 text-lg">{t.cta.subtitle}</p>
            <div className="flex flex-col sm:flex-row gap-4 mb-6 justify-center">
              <button
                onClick={() => window.open('https://hange.onrender.com/', '_blank')}
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 flex items-center justify-center space-x-2 font-semibold text-lg shadow-lg hover:shadow-xl"
              >
                <span>{t.cta.button}</span>
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
            <p className="text-sm text-gray-500">{t.cta.guarantee}</p>
            <p className="text-sm text-gray-400 mt-2">{t.hero.trusted}</p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-4 sm:px-6 lg:px-8 bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-5xl font-bold text-gray-900 mb-6">{t.features.title}</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">{t.features.subtitle}</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {t.features.items.map((feature, index) => (
              <div key={index} className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 border border-blue-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
                  <feature.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-4">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-5xl font-bold text-gray-900 mb-6">
              {language === 'et' ? 'Mida meie kliendid ütlevad' : 'What Our Clients Say'}
            </h2>
            <p className="text-xl text-gray-600">
              {language === 'et' ? 'Lugege, kuidas Hange AI on aidanud ettevõtetel edukalt osaleda riigihangetes' : 'Read how Hange AI has helped companies succeed in public procurement'}
            </p>
          </div>
          <div className="grid md:grid-cols-2 gap-8">
            {t.testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 border border-blue-100 shadow-lg hover:shadow-xl transition-shadow">
                <div className="flex mb-6">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-700 mb-8 italic leading-relaxed text-lg">&ldquo;{testimonial.text}&rdquo;</p>
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold mr-4">
                    {testimonial.name.charAt(0)}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{testimonial.name}</div>
                    <div className="text-gray-600 text-sm">{testimonial.role}</div>
                    <div className="text-gray-500 text-sm">{testimonial.company}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="max-w-4xl mx-auto text-center text-white">
          <h2 className="text-5xl font-bold mb-6">{t.cta.title}</h2>
          <p className="text-xl mb-12 opacity-90">{t.cta.subtitle}</p>
          <div className="flex flex-col sm:flex-row gap-4 max-w-lg mx-auto">
            <input
              type="email"
              placeholder={t.cta.placeholder}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1 px-6 py-4 rounded-xl text-gray-900 text-lg"
            />
            <button
              onClick={handleSignup}
              className="px-8 py-4 bg-white text-blue-600 rounded-xl hover:bg-gray-100 transition-colors font-semibold text-lg flex items-center justify-center space-x-2"
            >
              <span>{t.cta.button}</span>
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
          <p className="text-sm mt-6 opacity-75">{t.cta.guarantee}</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">H</span>
            </div>
            <span className="text-2xl font-bold">{t.title}</span>
          </div>
          <p className="text-gray-400 mb-6">
            {language === 'et' 
              ? '🤖 Hange AI poolt | Reaalajas andmed Eesti Riigihangete Registrist'
              : '🤖 Powered by Hange AI | Real-time data from Estonian Public Procurement Registry'
            }
          </p>
          <p className="text-gray-500">
            {language === 'et' 
              ? `© ${new Date().getFullYear()} Hange AI. Kõik õigused kaitstud.`
              : `© ${new Date().getFullYear()} Hange AI. All rights reserved.`
            }
          </p>
        </div>
      </footer>
    </div>
  )
}
