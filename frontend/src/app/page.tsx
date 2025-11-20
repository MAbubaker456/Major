'use client';

import { motion } from 'framer-motion';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ShaderAnimation } from '@/components/ShaderAnimation';
import Hero from "@/components/Hero";



// Lazy load sections below the fold for better performance
const FeaturesSection = dynamic(() => Promise.resolve(FeaturesComponent), { ssr: false });
const StatsSection = dynamic(() => Promise.resolve(StatsComponent), { ssr: false });
const CTASection = dynamic(() => Promise.resolve(CTAComponent), { ssr: false });
import { 
  Shield, 
  Zap, 
  Database, 
  Target, 
  GitBranch, 
  AlertTriangle,
  CheckCircle,
  ArrowRight,
  Github,
  Globe,
  Lock,
  TrendingUp
} from 'lucide-react';

const fadeInUp = {
  initial: { opacity: 0, y: 60 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 }
};

const staggerChildren = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};
function HeroSection() {
  return (
    <section className="relative min-h-screen overflow-hidden">
      <Hero
        headline={{
          line1: "AI-Powered",
          line2: "Red Team Testing",
        }}
        subtitle="CognitoForge simulates intelligent adversarial attacks on your code and CI/CD pipelines before real hackers do. Get proactive security insights with AI-driven vulnerability testing."
        trustBadge={{
          text: "Security-first teams love CognitoForge",
          icons: ["★", "★", "★"],
        }}
        buttons={{
          primary: {
            text: "Get Started Free",
            onClick: () => {
              // same as your old primary button
              window.location.href = "/demo";
            },
          },
          secondary: {
            text: "Learn More",
            onClick: () => {
              const el = document.getElementById("features");
              if (el) el.scrollIntoView({ behavior: "smooth" });
            },
          },
        }}
      />
    </section>
  );
}



function FeaturesComponent() {
  const features = [
    {
      icon: Target,
      title: "AI-Driven Attack Simulation",
      description: "Advanced machine learning models simulate real-world attack patterns and techniques used by sophisticated threat actors."
    },
    {
      icon: GitBranch,
      title: "CI/CD Pipeline Security",
      description: "Comprehensive analysis of your deployment pipelines to identify vulnerabilities before they reach production."
    },
    {
      icon: Shield,
      title: "Proactive Threat Detection",
      description: "Stay ahead of emerging threats with predictive security analysis and early warning systems."
    },
    {
      icon: Database,
      title: "Detailed Reporting",
      description: "Get actionable insights with comprehensive reports including attack paths, risk scores, and remediation strategies."
    }
  ];

  return (
    <section id="features" className="py-24 bg-black">
      <div className="container px-4 mx-auto">
        <motion.div 
          className="text-center mb-16"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-3xl md:text-5xl font-bold mb-4">
            Why Choose <span className="gradient-text">CognitoForge</span>?
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Advanced AI-powered security testing that goes beyond traditional vulnerability scanners
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 stagger-children">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className="glass-purple p-6 rounded-xl hover:bg-purple-500/10 transition-medium hover-lift group"
            >
              <feature.icon className="h-12 w-12 text-purple-400 mb-4 group-hover:text-purple-300 transition-colors" />
              <h3 className="text-xl font-semibold mb-3 text-purple-100">{feature.title}</h3>
              <p className="text-purple-300">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function StatsComponent() {
  const stats = [
    { label: "Vulnerabilities Detected", value: "10,000+", icon: AlertTriangle },
    { label: "Security Analyses", value: "5,000+", icon: TrendingUp },
    { label: "Active Users", value: "1,200+", icon: Shield },
    { label: "Attack Patterns", value: "500+", icon: Target }
  ];

  return (
    <section className="py-16 bg-black border-y border-purple-500/20">
      <div className="container px-4 mx-auto">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              className="text-center"
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <stat.icon className="h-8 w-8 text-primary mx-auto mb-2" />
              <div className="text-3xl font-bold text-primary mb-1">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CTAComponent() {
  return (
    <section className="py-24 relative overflow-hidden">
      {/* Pure black background with subtle purple accents */}
      <div className="absolute inset-0 bg-black" />
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/5 via-transparent to-purple-800/5" />
      
      <div className="container px-4 mx-auto text-center relative z-10">
        <div className="max-w-3xl mx-auto animate-fade-in-up">
          <h2 className="text-3xl md:text-5xl font-bold mb-6 text-purple-gradient">
            Ready to Secure Your Code?
          </h2>
          <p className="text-xl text-purple-300 mb-8">
            Join thousands of developers who trust CognitoForge to keep their applications secure
          </p>
          
          <div className="space-y-6">
            <Link href="/demo">
              <Button variant="purple" size="lg" className="text-lg px-8 glow-purple-medium">
                <Shield className="mr-2 h-5 w-5" />
                Get Started Free
              </Button>
            </Link>
            <div className="glass-purple p-6 rounded-xl max-w-md mx-auto">
              <div className="flex items-center gap-3 mb-3">
                <Shield className="h-5 w-5 text-purple-400" />
                <span className="text-sm text-purple-300">Enterprise-grade security</span>
              </div>
              <div className="flex items-center gap-3 mb-3">
                <Zap className="h-5 w-5 text-purple-400" />
                <span className="text-sm text-purple-300">Instant AI analysis</span>
              </div>
              <div className="flex items-center gap-3">
                <Database className="h-5 w-5 text-purple-400" />
                <span className="text-sm text-purple-300">Detailed reporting</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="fixed top-0 w-full z-50 glass-purple-strong border-b border-purple-500/20">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="text-xl font-bold text-purple-gradient hover-lift transition-fast">
              CognitoForge
            </Link>
            
            <nav className="hidden md:flex items-center space-x-8">
              <Link href="#features" className="text-purple-300 hover:text-purple-200 transition-fast">
                Features
              </Link>
              <Link href="/demo" className="text-purple-300 hover:text-purple-200 transition-fast">
                Demo
              </Link>
              <Link href="/demo">
                <Button variant="purple-outline" size="sm">
                  Get Started
                </Button>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <main>
        <HeroSection />
        <FeaturesSection />
        <StatsSection />
        <CTASection />
      </main>

      {/* Footer */}
      <footer className="border-t border-purple-800/30 py-12 bg-purple-950/50 glass-purple">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-purple-400 text-sm">
              © 2025 CognitoForge. All rights reserved.
            </div>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <Link href="#" className="text-purple-400 hover:text-purple-300 transition-fast">
                Privacy
              </Link>
              <Link href="#" className="text-purple-400 hover:text-purple-300 transition-fast">
                Terms
              </Link>
              <Link href="/docs" className="text-purple-400 hover:text-purple-300 transition-fast">
                Docs
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}