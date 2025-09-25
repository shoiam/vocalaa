"use client"

import { useState } from 'react'
import Link from 'next/link'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function BlogPage() {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const sampleConfig = `{
  "mcpServers": {
    "vocalaa-resume": {
      "command": "npx",
      "args": ["mcp-remote", "https://mcp.vocalaa.com/mcp/your-slug"]
    }
  }
}`

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 font-mono text-white">
      <nav className="p-6 border-b border-slate-700">
        <div className="container mx-auto flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold text-white hover:text-green-400 transition-colors">
            Vocalaa
          </Link>
          <div className="flex items-center space-x-4">
            <Link href="/dashboard" className="text-slate-300 hover:text-white transition-colors">
              Dashboard
            </Link>
            <Link href="/login" className="text-slate-300 hover:text-white transition-colors">
              Login
            </Link>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-12">
        <article className="max-w-4xl mx-auto">
          <div className="text-center space-y-6 mb-12">
            <h1 className="text-5xl font-bold">
              How to Connect Your Interactive Resume to Claude Desktop
            </h1>
            <p className="text-slate-300 text-xl max-w-3xl mx-auto">
              A step-by-step guide for recruiters and hiring managers to connect with your AI-powered resume using Claude Desktop
            </p>
            <div className="text-slate-400 text-sm">
              Published on {new Date().toLocaleDateString()}
            </div>
          </div>

          <div className="prose prose-slate prose-lg max-w-none text-slate-200">

            <section className="mb-12">
              <h2 className="text-3xl font-bold text-white mb-6">What is an Interactive Resume?</h2>
              <p className="text-slate-300 leading-relaxed mb-4">
                Traditional resumes are static documents that often fail to capture the full depth of a candidate&apos;s experience.
                Interactive resumes powered by Vocalaa transform your professional profile into an AI assistant that recruiters
                can have natural conversations with.
              </p>
              <p className="text-slate-300 leading-relaxed">
                Instead of scanning through pages of formatted text, you can simply ask questions like &quot;What&apos;s their Python experience?&quot;
                or &quot;Tell me about their leadership background&quot; and get detailed, contextual answers.
              </p>
            </section>

            <Card className="bg-slate-800/50 border-slate-600 mb-12">
              <CardHeader>
                <CardTitle className="text-white text-2xl">Prerequisites</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-slate-300">
                  <p className="mb-4">Before you begin, make sure you have:</p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li>Claude Desktop application installed on your computer</li>
                    <li>A valid Claude Pro or Claude for Work subscription</li>
                    <li>The candidate&apos;s MCP URL (they should have provided this to you)</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Step-by-step Guide */}
            <section className="mb-12">
              <h2 className="text-3xl font-bold text-white mb-8">Step-by-Step Connection Guide</h2>

              {/* Step 1 */}
              <div className="mb-10">
                <h3 className="text-2xl font-semibold text-green-400 mb-4">Step 1: Locate Your Claude Desktop Configuration</h3>
                <p className="text-slate-300 mb-4">
                  You need to add the MCP server configuration to Claude Desktop. The configuration file location depends on your operating system:
                </p>
                <div className="bg-slate-900 p-4 rounded-lg border border-slate-700 mb-4">
                  <div className="space-y-2 text-sm font-mono">
                    <div><span className="text-yellow-400">macOS:</span> <span className="text-green-400">~/Library/Application Support/Claude/claude_desktop_config.json</span></div>
                    <div><span className="text-yellow-400">Windows:</span> <span className="text-green-400">%APPDATA%/Claude/claude_desktop_config.json</span></div>
                  </div>
                </div>
              </div>

              {/* Step 2 */}
              <div className="mb-10">
                <h3 className="text-2xl font-semibold text-green-400 mb-4">Step 2: Add the MCP Server Configuration</h3>
                <p className="text-slate-300 mb-4">
                  Open the configuration file in a text editor and add the following configuration. Replace
                  <span className="bg-slate-800 px-2 py-1 rounded text-yellow-400 font-mono mx-1">your-slug</span>
                  with the actual slug provided by the candidate:
                </p>

                <Card className="bg-slate-900 border-slate-600 mb-4">
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400 text-sm">claude_desktop_config.json</span>
                      <Button
                        onClick={() => copyToClipboard(sampleConfig)}
                        size="sm"
                        variant="ghost"
                        className="text-slate-400 hover:text-white"
                      >
                        {copied ? 'Copied!' : 'Copy'}
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <pre className="text-green-400 text-sm overflow-x-auto">
{sampleConfig}
                    </pre>
                  </CardContent>
                </Card>

                <div className="bg-blue-900/20 border border-blue-700 p-4 rounded-lg">
                  <div className="flex items-start space-x-2">
                    <div className="text-blue-400 mt-1">ℹ️</div>
                    <div className="text-blue-200 text-sm">
                      <strong>Important:</strong> If your configuration file is empty, make sure to wrap the entire configuration in curly braces as shown above.
                      If you already have other MCP servers configured, just add the &quot;vocalaa-resume&quot; entry to your existing &quot;mcpServers&quot; object.
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 3 */}
              <div className="mb-10">
                <h3 className="text-2xl font-semibold text-green-400 mb-4">Step 3: Restart Claude Desktop</h3>
                <p className="text-slate-300 mb-4">
                  After saving the configuration file, completely close and restart Claude Desktop for the changes to take effect.
                </p>
              </div>

              {/* Step 4 */}
              <div className="mb-10">
                <h3 className="text-2xl font-semibold text-green-400 mb-4">Step 4: Start Conversations</h3>
                <p className="text-slate-300 mb-4">
                  Once connected, you can start asking questions about the candidate. Here are some example questions to get you started:
                </p>

                <Card className="bg-slate-800/30 border-slate-600">
                  <CardHeader>
                    <CardTitle className="text-white text-lg">Sample Questions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3 text-slate-300">
                      <li className="flex items-start space-x-2">
                        <span className="text-green-400 mt-1">•</span>
                        <span>&quot;What programming languages does this candidate know?&quot;</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="text-green-400 mt-1">•</span>
                        <span>&quot;Tell me about their most recent work experience&quot;</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="text-green-400 mt-1">•</span>
                        <span>&quot;What projects have they built with React?&quot;</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="text-green-400 mt-1">•</span>
                        <span>&quot;Describe their leadership experience&quot;</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <span className="text-green-400 mt-1">•</span>
                        <span>&quot;What&apos;s their educational background?&quot;</span>
                      </li>
                    </ul>
                  </CardContent>
                </Card>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold text-white mb-6">Troubleshooting</h2>

              <div className="space-y-6">
                <Card className="bg-red-900/20 border-red-700">
                  <CardHeader>
                    <CardTitle className="text-red-400">Connection Issues</CardTitle>
                  </CardHeader>
                  <CardContent className="text-slate-300">
                    <p className="mb-2"><strong>Problem:</strong> Claude Desktop doesn&apos;t recognize the MCP server</p>
                    <p><strong>Solution:</strong> Double-check the JSON syntax in your configuration file and ensure you&apos;ve restarted Claude Desktop completely.</p>
                  </CardContent>
                </Card>

                <Card className="bg-yellow-900/20 border-yellow-700">
                  <CardHeader>
                    <CardTitle className="text-yellow-400">Invalid MCP URL</CardTitle>
                  </CardHeader>
                  <CardContent className="text-slate-300">
                    <p className="mb-2"><strong>Problem:</strong> The MCP URL doesn&apos;t work</p>
                    <p><strong>Solution:</strong> Verify the URL with the candidate and ensure it matches exactly what they provided.</p>
                  </CardContent>
                </Card>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-3xl font-bold text-white mb-6">Why Use Interactive Resumes?</h2>
              <div className="grid md:grid-cols-2 gap-6">
                <Card className="bg-slate-800/30 border-slate-600">
                  <CardHeader>
                    <CardTitle className="text-green-400">For Recruiters</CardTitle>
                  </CardHeader>
                  <CardContent className="text-slate-300">
                    <ul className="space-y-2 list-disc list-inside">
                      <li>Ask specific, targeted questions</li>
                      <li>Get instant, detailed responses</li>
                      <li>No more scanning through lengthy PDFs</li>
                      <li>Discover relevant skills quickly</li>
                    </ul>
                  </CardContent>
                </Card>

                <Card className="bg-slate-800/30 border-slate-600">
                  <CardHeader>
                    <CardTitle className="text-blue-400">For Candidates</CardTitle>
                  </CardHeader>
                  <CardContent className="text-slate-300">
                    <ul className="space-y-2 list-disc list-inside">
                      <li>Stand out from traditional resumes</li>
                      <li>Showcase personality and communication</li>
                      <li>Always available for questions</li>
                      <li>No formatting headaches</li>
                    </ul>
                  </CardContent>
                </Card>
              </div>
            </section>

            <section className="text-center bg-gradient-to-r from-green-900/20 to-blue-900/20 border border-green-700/30 rounded-lg p-8">
              <h2 className="text-3xl font-bold text-white mb-4">Ready to Create Your Own Interactive Resume?</h2>
              <p className="text-slate-300 mb-6 max-w-2xl mx-auto">
                Join the future of professional networking. Transform your static resume into an AI-powered assistant that recruiters can actually talk to.
              </p>
              <div className="space-x-4">
                <Link href="/dashboard">
                  <Button className="bg-green-600 hover:bg-green-700 text-white px-8 py-3">
                    Create Your Resume
                  </Button>
                </Link>
                <Link href="/">
                  <Button variant="outline" className="border-slate-500 text-slate-300 hover:bg-slate-800 px-8 py-3">
                    Learn More
                  </Button>
                </Link>
              </div>
            </section>
          </div>
        </article>
      </main>
    </div>
  )
}