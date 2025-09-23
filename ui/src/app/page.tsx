import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white font-mono">
      <nav className="p-6 flex justify-between items-center">
        <h1 className="text-2xl font-bold">Vocalaa</h1>
        <div className="flex items-center space-x-4">
          <Link href="/blog" className="text-slate-300 hover:text-white transition-colors">
            How It Works
          </Link>
          <Link href="/login">
            <Button variant="ghost" className="text-white hover:text-slate-300">
              Login
            </Button>
          </Link>
          <Link href="/login">
            <Button className="bg-green-600 hover:bg-green-700">
              Get Started
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="container mx-auto px-6 py-20 text-center">
        <div className="max-w-4xl mx-auto space-y-8">
          
          {/* Main Headline */}
          <h1 className="text-5xl md:text-7xl font-bold leading-tight">
            Ditch the PDF.<br />
            <span className="text-green-400">Your resume just got superpowers.</span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl md:text-2xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
            Stop sending static resumes. Let recruiters ask exactly what they want to know. 
            Turn your professional profile into an AI assistant that actually understands your experience.
          </p>

          {/* Problem/Solution */}
          <div className="grid md:grid-cols-2 gap-8 py-12">
            <Card className="bg-red-900/20 border-red-800">
              <CardHeader>
                <CardTitle className="text-red-400 text-left">The Old Way</CardTitle>
              </CardHeader>
              <CardContent className="text-left space-y-2 text-slate-300">
                <p>📄 Static PDF that everyone ignores</p>
                <p>❓ Recruiters can&apos;t ask specific questions</p>
                <p>📧 Endless back-and-forth emails</p>
                <p>🔍 Your skills get lost in the noise</p>
              </CardContent>
            </Card>

            <Card className="bg-green-900/20 border-green-800">
              <CardHeader>
                <CardTitle className="text-green-400 text-left">The Vocalaa Way</CardTitle>
              </CardHeader>
              <CardContent className="text-left space-y-2 text-slate-300">
                <p>💬 Interactive conversations about your experience</p>
                <p>🎯 Recruiters ask exactly what matters to them</p>
                <p>⚡ Instant, intelligent responses 24/7</p>
                <p>🚀 Stand out from the static resume pile</p>
              </CardContent>
            </Card>
          </div>

          {/* CTA */}
          <div className="space-y-4">
            <Link href="/login">
              <Button size="lg" className="bg-green-600 hover:bg-green-700 text-lg px-8 py-4">
                Create Your Interactive MCP Resume
              </Button>
            </Link>
            <p className="text-sm text-slate-400">
              Join the resume revolution. Takes 5 minutes to set up.
            </p>
          </div>

          {/* Tutorial Link */}
          <div className="bg-slate-800/30 border border-slate-600 rounded-lg p-6 max-w-2xl mx-auto">
            <p className="text-slate-300 mb-4">
              <strong>For Recruiters:</strong> Learn how to connect and interact with interactive resumes
            </p>
            <Link href="/blog">
              <Button className="bg-green-600 hover:bg-green-700 text-white">
                📚 View Setup Tutorial
              </Button>
            </Link>
          </div>

          {/* Demo Example */}
          <div className="pt-16">
            <h3 className="text-2xl font-semibold mb-8 text-slate-300">See it in action:</h3>
            <Card className="bg-slate-800/50 border-slate-700 text-left max-w-2xl mx-auto">
              <CardContent className="p-6 space-y-4">
                <div className="border-l-4 border-blue-500 pl-4">
                  <p className="text-blue-400 font-semibold">Recruiter asks:</p>
                  <p className="text-slate-300">&quot;What&apos;s their Python experience like?&quot;</p>
                </div>
                <div className="border-l-4 border-green-500 pl-4">
                  <p className="text-green-400 font-semibold">Your Vocalaa responds:</p>
                  <p className="text-slate-300">&quot;5+ years Python experience including FastAPI, Django, and data analysis. Built 12 production applications serving 10k+ users...&quot;</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}