'use client'

import { useState } from 'react'
import { ChevronRight, Search, FileText, Mail, BarChart3 } from 'lucide-react'

export default function Home() {
  const [language, setLanguage] = useState<'et' | 'en'>('et')
  const [email, setEmail] = useState('')

  const content = {
    et: {
      title: 'Hange AI',
      subtitle: 'Eesti Riigihanke Intelligentsuse Platvorm',
      description: 'AI-põhine riigihangete otsing intelligentsete ülevaadete ja automatiseeritud dokumenditöötlusega',
      features: {
        title: 'Peamised funktsioonid',
        items: [
          {
            icon: Search,
            title: 'Intelligentne otsing',
            description: 'AI-põhine riigihangete avastamine reaalajas RSS-voo abil'
          },
          {
            icon: FileText,
            title: 'Dokumenditöötlus',
            description: 'OpenAI-põhine vormiväljade ekstrakteerimine 90% täpsusega'
          },
          {
            icon: Mail,
            title: 'E-posti teavitused',
            description: 'Isikupärastatud hoiatused sektoripõhise filtreerimisega'
          },
          {
            icon: BarChart3,
            title: 'Analüütika',
            description: 'Interaktiivsed diagrammid ja riigihangete statistika'
          }
        ]
      },
      stats: [
        { number: '712+', label: 'Aktiivset hanget' },
        { number: '90%', label: 'AI täpsus' },
        { number: '10x', label: 'Kiirem töötlemine' },
        { number: '24/7', label: 'Reaalajas andmed' }
      ],
      cta: {
        title: 'Alusta täna',
        subtitle: 'Liitu tuhandete ettevõtetega, kes kasutavad Hange AI-d',
        button: 'Registreeru tasuta',
        placeholder: 'sinu.email@näide.com'
      }
    },
    en: {
      title: 'Hange AI',
      subtitle: 'Estonian Procurement Intelligence Platform',
      description: 'AI-powered procurement search with intelligent insights and automated document processing',
      features: {
        title: 'Key Features',
        items: [
          {
            icon: Search,
            title: 'Intelligent Search',
            description: 'AI-powered procurement discovery with real-time RSS feed'
          },
          {
            icon: FileText,
            title: 'Document Processing',
            description: 'OpenAI-powered form field extraction with 90% accuracy'
          },
          {
            icon: Mail,
            title: 'Email Notifications',
            description: 'Personalized alerts with sector-based filtering'
          },
          {
            icon: BarChart3,
            title: 'Analytics',
            description: 'Interactive charts and procurement statistics'
          }
        ]
      },
      stats: [
        { number: '712+', label: 'Active Procurements' },
        { number: '90%', label: 'AI Accuracy' },
        { number: '10x', label: 'Faster Processing' },
        { number: '24/7', label: 'Real-time Data' }
      ],
      cta: {
        title: 'Start Today',
        subtitle: 'Join thousands of companies using Hange AI',
        button: 'Sign Up Free',
        placeholder: 'your.email@example.com'
      }
    }
  }

  const t = content[language]

  const handleSignup = () => {
    if (email) {
      window.open(`https://hange-ai.streamlit.app/?email=${encodeURIComponent(email)}`, '_blank')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-blue-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">H</span>
              </div>
              <span className="text-xl font-bold text-gray-900">{t.title}</span>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setLanguage('et')}
                className={`px-3 py-1 rounded ${language === 'et' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                EST
              </button>
              <button
                onClick={() => setLanguage('en')}
                className={`px-3 py-1 rounded ${language === 'en' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                ENG
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              {t.title}
            </span>
          </h1>
          <h2 className="text-2xl md:text-3xl text-gray-700 mb-8">{t.subtitle}</h2>
          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">{t.description}</p>
          
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
            {t.stats.map((stat, index) => (
              <div key={index} className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-blue-200">
                <div className="text-3xl font-bold text-blue-600 mb-2">{stat.number}</div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>

          {/* CTA */}
          <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-8 border border-blue-200 max-w-md mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">{t.cta.title}</h3>
            <p className="text-gray-600 mb-6">{t.cta.subtitle}</p>
            <div className="flex flex-col sm:flex-row gap-4">
              <input
                type="email"
                placeholder={t.cta.placeholder}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={handleSignup}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 flex items-center justify-center space-x-2"
              >
                <span>{t.cta.button}</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white/40 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">{t.features.title}</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {t.features.items.map((feature, index) => (
              <div key={index} className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-blue-200 hover:shadow-lg transition-shadow">
                <feature.icon className="w-12 h-12 text-blue-600 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-2 mb-6">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">H</span>
            </div>
            <span className="text-xl font-bold">{t.title}</span>
          </div>
          <p className="text-gray-400 mb-6">
            {language === 'et' 
              ? '🤖 Hange AI poolt | Reaalajas andmed Eesti Riigihangete Registrist'
              : '🤖 Powered by Hange AI | Real-time data from Estonian Public Procurement Registry'
            }
          </p>
          <p className="text-gray-500">
            {language === 'et' 
              ? `Viimati uuendatud: ${new Date().toLocaleDateString('et-EE')}`
              : `Last updated: ${new Date().toLocaleDateString('en-US')}`
            }
          </p>
        </div>
      </footer>
    </div>
  )
}
