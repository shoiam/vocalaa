/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/no-explicit-any */
"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { User } from '@supabase/supabase-js'
import { getCurrentUser, signOut } from '@/lib/auth'
import { createProfile, updateProfile, getProfile } from '@/lib/api'
import { supabase } from '@/lib/supabase'
import { ProfileForm } from '@/components/ProfileForm'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Toaster } from "@/components/ui/sonner"
import { toast } from "sonner"
import Link from 'next/link'

interface ProfileFormData {
  basic_info: {
    name: string
    title: string
    email: string
    summary: string
    location?: string
  }
  work_experience: Array<{
    company: string
    role: string
    duration: string
    description: string
    achievements?: string[]
    technologies?: string[]
  }>
  skills: {
    programming_languages: string[]
    frameworks: string[]
    databases: string[]
  }
  projects: Array<{
    name: string
    description: string
    technologies: string[]
    github_url?: string
    demo_url?: string
  }>
  education: Array<{
    institution: string
    degree: string
    field: string
    graduation_year?: number
  }>
}

interface ProfileCreationResult {
  mcp_slug: string
  mcp_url: string
  profile_id: string
}

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [profileResult, setProfileResult] = useState<ProfileCreationResult | null>(null)
  const [existingProfile, setExistingProfile] = useState<any>(null)
  const [originalProfile, setOriginalProfile] = useState<any>(null)
  const [error, setError] = useState('')
  const router = useRouter()

  useEffect(() => {
    const checkAuth = async () => {
      console.log('Dashboard: Starting auth check...')
      try {
        const token = localStorage.getItem('access_token')
        const userEmail = localStorage.getItem('user_email')
        console.log('Dashboard: Token exists:', !!token, 'Email:', userEmail)

        if (token && userEmail) {
          // Create a user-like object for compatibility
          setUser({ email: userEmail } as User)

          // Check for existing profile
          console.log('Dashboard: About to check existing profile...')
          await checkExistingProfile(token)
        } else {
          console.log('Dashboard: No token/email, redirecting to login')
          router.push('/login')
        }
      } catch (error) {
        console.log('Dashboard: Auth error:', error)
        router.push('/login')
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [router])

  const checkExistingProfile = async (token: string) => {
    console.log('Checking for existing profile...')
    try {
      const existingProfileData = await getProfile(token)
      console.log('Profile response:', existingProfileData)
      if (existingProfileData) {
        const formattedProfile = {
          basic_info: existingProfileData.basic_info,
          work_experience: existingProfileData.work_experience,
          skills: {
            programming_languages: Array.isArray(existingProfileData.skills.programming_languages)
              ? existingProfileData.skills.programming_languages.join(', ')
              : existingProfileData.skills.programming_languages,
            frameworks: Array.isArray(existingProfileData.skills.frameworks)
              ? existingProfileData.skills.frameworks.join(', ')
              : existingProfileData.skills.frameworks,
            databases: Array.isArray(existingProfileData.skills.databases)
              ? existingProfileData.skills.databases.join(', ')
              : existingProfileData.skills.databases,
          },
          projects: existingProfileData.projects.map((project: any) => ({
            ...project,
            technologies: Array.isArray(project.technologies)
              ? project.technologies.join(', ')
              : project.technologies
          })),
          education: existingProfileData.education
        }

        setOriginalProfile(existingProfileData)
        setExistingProfile(formattedProfile)
        setProfileResult({
          mcp_slug: existingProfileData.mcp_slug,
          mcp_url: existingProfileData.mcp_url,
          profile_id: existingProfileData.profile_id
        })
      }
    } catch (error) {
      console.log('No existing profile found - new user', error)
    }
  }

  const convertSkillString = (skillString: unknown): string[] => {
    if (typeof skillString === 'string' && skillString.trim()) {
      return skillString.split(',').map(s => s.trim()).filter(s => s)
    }
    if (Array.isArray(skillString)) {
      return skillString
    }
    return []
  }

  const convertProjectTechnologies = (technologies: unknown): string[] => {
    if (typeof technologies === 'string' && technologies.trim()) {
      return technologies.split(',').map(s => s.trim()).filter(s => s)
    }
    if (Array.isArray(technologies)) {
      return technologies
    }
    return []
  }
  const handleProfileSubmit = async (formData: ProfileFormData) => {
    setSubmitting(true)
    setError('')

    try {
      const token = localStorage.getItem('access_token')

      if (!token) {
        throw new Error('No authentication token found')
      }
      const processedData = {
        basic_info: formData.basic_info,
        work_experience: formData.work_experience,
        skills: {
          programming_languages: convertSkillString(formData.skills.programming_languages),
          frameworks: convertSkillString(formData.skills.frameworks),
          databases: convertSkillString(formData.skills.databases),
        },
        projects: formData.projects.map(project => ({
          ...project,
          technologies: convertProjectTechnologies(project.technologies)
        })),
        education: formData.education
      }
      const result = existingProfile
        ? await updateProfile(processedData, token)
        : await createProfile(processedData, token)

      setProfileResult(result)
      toast.success(existingProfile
        ? 'Profile updated successfully!'
        : 'Profile created successfully!'
      )

    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save profile'
      setError(errorMessage)
      toast.error(errorMessage)

      console.error('Profile save error:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const handleSignOut = async () => {
    try {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_id')
      localStorage.removeItem('user_email')
      router.push('/')
    } catch (error) {
      console.error('Error signing out:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center font-mono">
        <div className="text-white text-xl">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 font-mono text-white">
      <nav className="p-6 flex justify-between items-center border-b border-slate-700">
        <h1 className="text-2xl font-bold">Vocalaa Dashboard</h1>
        <div className="flex items-center space-x-4">
          <span className="text-slate-400">Welcome, {user?.email}</span>
          <Button onClick={handleSignOut} variant="ghost" className="text-white">
            Sign Out
          </Button>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-12">
        {profileResult ? (
          <SuccessPage
            result={profileResult}
            existingProfile={existingProfile}
            onEditProfile={() => setProfileResult(null)}
          />
        ) : (
          <>
            <div className="text-center space-y-6 mb-12">
              <h2 className="text-4xl font-bold">
                {existingProfile ? 'Update Your Interactive Resume' : 'Create Your Interactive Resume'}
              </h2>
              <p className="text-slate-300 text-lg max-w-2xl mx-auto">
                {existingProfile
                  ? 'Update your profile information below. Changes will be reflected in your MCP URL.'
                  : 'Skip the formatting headaches of static resumes. Fill out the form below to transform your traditional resume into an AI-powered assistant that recruiters can interact with conversationally.'
                }
              </p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-900/20 border border-red-800 rounded-lg text-red-400 text-center">
                {error}
              </div>
            )}

            <ProfileForm
              onSubmit={handleProfileSubmit}
              loading={submitting}
              initialData={existingProfile}
              isEditing={!!existingProfile}
              onCancel={originalProfile ? () => setProfileResult({
                mcp_slug: originalProfile.mcp_slug,
                mcp_url: originalProfile.mcp_url,
                profile_id: originalProfile.profile_id
              }) : undefined}
            />
          </>
        )}
      </main>
      <Toaster />
    </div>
  )
}

function SuccessPage({ result, existingProfile, onEditProfile }: { result: ProfileCreationResult; existingProfile?: any; onEditProfile?: () => void }) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const connectionConfig = `{
  "mcpServers": {
    "vocalaa-resume": {
      "command": "npx",
      "args": ["mcp-remote", "${result.mcp_url}"]
    }
  }
}`


  return (
    <div className="max-w-4xl mx-auto text-center space-y-8">
      <div className="space-y-4">
        <h2 className="text-4xl font-bold text-green-400">
          {existingProfile ? 'Your Interactive Resume' : 'Your Interactive Resume is Live!'}
        </h2>
        <p className="text-xl text-slate-300">
          {existingProfile
            ? 'Your resume is live and ready to share with recruiters.'
            : 'Your resume has been transformed into an AI assistant. Share your MCP URL with recruiters.'
          }
        </p>
        {existingProfile && onEditProfile && (
          <Button
            onClick={onEditProfile}
            className="bg-blue-600 hover:bg-blue-700 mt-4"
          >
            Edit Profile
          </Button>
        )}
      </div>

      <Card className="bg-slate-800/50 border-slate-700 text-left">
        <CardHeader>
          <CardTitle className="text-white">Your MCP URL</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-2">
            <code className="flex-1 bg-slate-900 p-3 rounded text-green-400 font-mono">
              {result.mcp_url}
            </code>
            <Button 
              onClick={() => copyToClipboard(result.mcp_url)}
              size="sm"
              className="bg-green-600 hover:bg-green-700"
            >
              {copied ? 'Copied!' : 'Copy'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-slate-800/50 border-slate-700 text-left">
        <CardHeader>
          <CardTitle className="text-white">For Recruiters: Connection Instructions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-slate-300">
            Share these instructions with recruiters to connect to your interactive resume:
          </p>

          <div className="bg-blue-900/20 border border-blue-700 p-3 rounded-lg">
            <p className="text-blue-200 text-sm mb-2">
              📚 <strong>Need detailed instructions?</strong>
            </p>
            <p className="text-blue-300 text-sm">
              Share our complete tutorial: <Link href="/blog" className="underline hover:text-blue-100">vocalaa.com/blog</Link>
            </p>
          </div>
          
          <div className="space-y-2">
            <p className="text-slate-400 text-sm">Add to Claude Desktop configuration:</p>
            <pre className="bg-slate-900 p-4 rounded text-sm text-green-400 overflow-x-auto">
{connectionConfig}
            </pre>
          </div>

          <Button 
            onClick={() => copyToClipboard(connectionConfig)}
            className="w-full bg-green-600 hover:bg-green-700"
          >
            Copy Configuration
          </Button>
        </CardContent>
      </Card>

      <div className="text-slate-400 text-sm space-y-2">
        <p>Once connected, recruiters can ask questions like:</p>
        <ul className="list-disc list-inside space-y-1 max-w-md mx-auto">
          <li>&quot;What&apos;s their Python experience?&quot;</li>
          <li>&quot;Tell me about their leadership background&quot;</li>
          <li>&quot;What projects have they built?&quot;</li>
        </ul>
      </div>
    </div>
  )
}