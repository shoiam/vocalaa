"use client"

// import { useState } from 'react'
import { useForm, useFieldArray, Controller } from 'react-hook-form'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Plus, Trash2 } from 'lucide-react'

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

interface ProfileFormProps {
  onSubmit: (data: ProfileFormData) => Promise<void>
  initialData?: Partial<ProfileFormData>
  loading?: boolean
  isEditing?: boolean
  onCancel?: () => void
}

export function ProfileForm({ onSubmit, initialData, loading, isEditing = false, onCancel }: ProfileFormProps) {
  const { register, control, handleSubmit, formState: { errors } } = useForm<ProfileFormData>({
    defaultValues: initialData || {
      basic_info: { name: '', title: '', email: '', summary: '', location: '' },
      work_experience: [{ company: '', role: '', duration: '', description: '', achievements: [], technologies: [] }],
      skills: { programming_languages: [], frameworks: [], databases: [] },
      projects: [{ name: '', description: '', technologies: [], github_url: '', demo_url: '' }],
      education: [{ institution: '', degree: '', field: '', graduation_year: undefined }]
    }
  })

  const { fields: workFields, append: appendWork, remove: removeWork } = useFieldArray({
    control,
    name: "work_experience"
  })

  const { fields: projectFields, append: appendProject, remove: removeProject } = useFieldArray({
    control,
    name: "projects"
  })

  const { fields: educationFields, append: appendEducation, remove: removeEducation } = useFieldArray({
    control,
    name: "education"
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 max-w-4xl mx-auto">
      
      {/* Basic Information */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Basic Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-slate-300">Full Name</Label>
              <Input
                {...register("basic_info.name", { required: "Name is required" })}
                className="bg-slate-700 border-slate-600 text-white"
                placeholder="John Doe"
              />
              {errors.basic_info?.name && <p className="text-red-400 text-sm mt-1">{errors.basic_info.name.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="title" className="text-slate-300">Professional Title</Label>
              <Input
                {...register("basic_info.title", { required: "Title is required" })}
                className="bg-slate-700 border-slate-600 text-white"
                placeholder="Software Engineer"
              />
              {errors.basic_info?.title && <p className="text-red-400 text-sm mt-1">{errors.basic_info.title.message}</p>}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-slate-300">Email</Label>
              <Input
                {...register("basic_info.email", { required: "Email is required" })}
                type="email"
                className="bg-slate-700 border-slate-600 text-white"
                placeholder="john@example.com"
              />
              {errors.basic_info?.email && <p className="text-red-400 text-sm mt-1">{errors.basic_info.email.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="location" className="text-slate-300">Location (Optional)</Label>
              <Input
                {...register("basic_info.location")}
                className="bg-slate-700 border-slate-600 text-white"
                placeholder="San Francisco, CA"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="summary" className="text-slate-300">Professional Summary</Label>
            <Textarea
              {...register("basic_info.summary", { required: "Summary is required" })}
              className="bg-slate-700 border-slate-600 text-white min-h-24"
              placeholder="Brief description of your professional background and expertise..."
            />
            {errors.basic_info?.summary && <p className="text-red-400 text-sm mt-1">{errors.basic_info.summary.message}</p>}
          </div>
        </CardContent>
      </Card>

      {/* Work Experience */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-white">Work Experience</CardTitle>
          <Button
            type="button"
            onClick={() => appendWork({ company: '', role: '', duration: '', description: '', achievements: [], technologies: [] })}
            size="sm"
            className="bg-green-600 hover:bg-green-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Job
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {workFields.map((field, index) => (
            <div key={field.id} className="border border-slate-600 rounded-lg p-4 bg-slate-900/30">
              <div className="flex justify-between items-center mb-4">
                <h4 className="text-slate-300 font-medium">Position {index + 1}</h4>
                {workFields.length > 1 && (
                  <Button
                    type="button"
                    onClick={() => removeWork(index)}
                    size="sm"
                    variant="outline"
                    className="text-red-400 border-red-400 hover:bg-red-400 hover:text-white"
                  >
                    <Trash2 className="w-4 h-4 mr-1" />
                    Remove
                  </Button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="space-y-2">
                  <Label className="text-slate-300">Company</Label>
                  <Input
                    {...register(`work_experience.${index}.company` as const, { required: "Company is required" })}
                    className="bg-slate-700 border-slate-600 text-white"
                    placeholder="Company Name"
                  />
                  {errors.work_experience?.[index]?.company && (
                    <p className="text-red-400 text-sm mt-1">{errors.work_experience[index]?.company?.message}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Role</Label>
                  <Input
                    {...register(`work_experience.${index}.role` as const, { required: "Role is required" })}
                    className="bg-slate-700 border-slate-600 text-white"
                    placeholder="Job Title"
                  />
                  {errors.work_experience?.[index]?.role && (
                    <p className="text-red-400 text-sm mt-1">{errors.work_experience[index]?.role?.message}</p>
                  )}
                </div>
              </div>

              <div className="mb-4 space-y-2">
                <Label className="text-slate-300">Duration</Label>
                <Input
                  {...register(`work_experience.${index}.duration` as const, { required: "Duration is required" })}
                  className="bg-slate-700 border-slate-600 text-white"
                  placeholder="Jan 2020 - Present"
                />
                {errors.work_experience?.[index]?.duration && (
                  <p className="text-red-400 text-sm mt-1">{errors.work_experience[index]?.duration?.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label className="text-slate-300">Description</Label>
                <Textarea
                  {...register(`work_experience.${index}.description` as const, { required: "Description is required" })}
                  className="bg-slate-700 border-slate-600 text-white min-h-20"
                  placeholder="Describe your responsibilities and accomplishments..."
                />
                {errors.work_experience?.[index]?.description && (
                  <p className="text-red-400 text-sm mt-1">{errors.work_experience[index]?.description?.message}</p>
                )}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Skills */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Skills</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label className="text-slate-300">Programming Languages</Label>
            <Input
              {...register("skills.programming_languages")}
              className="bg-slate-700 border-slate-600 text-white"
              placeholder="Python, JavaScript, Java (comma separated)"
            />
          </div>
          <div className="space-y-2">
            <Label className="text-slate-300">Frameworks & Libraries</Label>
            <Input
              {...register("skills.frameworks")}
              className="bg-slate-700 border-slate-600 text-white"
              placeholder="React, Django, FastAPI (comma separated)"
            />
          </div>
          <div className="space-y-2">
            <Label className="text-slate-300">Databases & Tools</Label>
            <Input
              {...register("skills.databases")}
              className="bg-slate-700 border-slate-600 text-white"
              placeholder="PostgreSQL, MongoDB, Docker (comma separated)"
            />
          </div>
        </CardContent>
      </Card>

      {/* Projects */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-white">Projects</CardTitle>
          <Button
            type="button"
            onClick={() => appendProject({ name: '', description: '', technologies: [], github_url: '', demo_url: '' })}
            size="sm"
            className="bg-green-600 hover:bg-green-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Project
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {projectFields.map((field, index) => (
            <div key={field.id} className="border border-slate-600 rounded-lg p-4 bg-slate-900/30">
              <div className="flex justify-between items-center mb-4">
                <h4 className="text-slate-300 font-medium">Project {index + 1}</h4>
                {projectFields.length > 1 && (
                  <Button
                    type="button"
                    onClick={() => removeProject(index)}
                    size="sm"
                    variant="outline"
                    className="text-red-400 border-red-400 hover:bg-red-400 hover:text-white"
                  >
                    <Trash2 className="w-4 h-4 mr-1" />
                    Remove
                  </Button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="space-y-2">
                  <Label className="text-slate-300">Project Name</Label>
                  <Input
                    {...register(`projects.${index}.name` as const, { required: "Project name is required" })}
                    className="bg-slate-700 border-slate-600 text-white"
                    placeholder="Project Name"
                  />
                  {errors.projects?.[index]?.name && (
                    <p className="text-red-400 text-sm mt-1">{errors.projects[index]?.name?.message}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Technologies Used</Label>
                  <Input
                    {...register(`projects.${index}.technologies` as const)}
                    className="bg-slate-700 border-slate-600 text-white"
                    placeholder="React, Node.js, MongoDB (comma separated)"
                  />
                </div>
              </div>

              <div className="mb-4 space-y-2">
                <Label className="text-slate-300">Description</Label>
                <Textarea
                  {...register(`projects.${index}.description` as const, { required: "Description is required" })}
                  className="bg-slate-700 border-slate-600 text-white min-h-20"
                  placeholder="Describe what this project does and your role in it..."
                />
                {errors.projects?.[index]?.description && (
                  <p className="text-red-400 text-sm mt-1">{errors.projects[index]?.description?.message}</p>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-slate-300">GitHub URL (Optional)</Label>
                  <Input
                    {...register(`projects.${index}.github_url` as const)}
                    className="bg-slate-700 border-slate-600 text-white"
                    placeholder="https://github.com/username/project"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Demo URL (Optional)</Label>
                  <Input
                    {...register(`projects.${index}.demo_url` as const)}
                    className="bg-slate-700 border-slate-600 text-white"
                    placeholder="https://project-demo.com"
                  />
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Education */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-white">Education</CardTitle>
          <Button
            type="button"
            onClick={() => appendEducation({ institution: '', degree: '', field: '', graduation_year: undefined })}
            size="sm"
            className="bg-green-600 hover:bg-green-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Education
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {educationFields.map((field, index) => (
            <div key={field.id} className="border border-slate-600 rounded-lg p-4 bg-slate-900/30">
              <div className="flex justify-between items-center mb-4">
                <h4 className="text-slate-300 font-medium">Education {index + 1}</h4>
                {educationFields.length > 1 && (
                  <Button
                    type="button"
                    onClick={() => removeEducation(index)}
                    size="sm"
                    variant="outline"
                    className="text-red-400 border-red-400 hover:bg-red-400 hover:text-white"
                  >
                    <Trash2 className="w-4 h-4 mr-1" />
                    Remove
                  </Button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="space-y-2">
                  <Label className="text-slate-300">Institution</Label>
                  <Input
                    {...register(`education.${index}.institution` as const, { required: "Institution is required" })}
                    className="bg-slate-700 border-slate-600 text-white"
                    placeholder="University Name"
                  />
                  {errors.education?.[index]?.institution && (
                    <p className="text-red-400 text-sm mt-1">{errors.education[index]?.institution?.message}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Degree</Label>
                  <Input
                    {...register(`education.${index}.degree` as const, { required: "Degree is required" })}
                    className="bg-slate-700 border-slate-600 text-white"
                    placeholder="Bachelor of Science"
                  />
                  {errors.education?.[index]?.degree && (
                    <p className="text-red-400 text-sm mt-1">{errors.education[index]?.degree?.message}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-slate-300">Field of Study</Label>
                  <Input
                    {...register(`education.${index}.field` as const, { required: "Field is required" })}
                    className="bg-slate-700 border-slate-600 text-white"
                    placeholder="Computer Science"
                  />
                  {errors.education?.[index]?.field && (
                    <p className="text-red-400 text-sm mt-1">{errors.education[index]?.field?.message}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Graduation Year (Optional)</Label>
                  <Controller
                    name={`education.${index}.graduation_year` as const}
                    control={control}
                    render={({ field }) => (
                      <Select onValueChange={(value) => field.onChange(value ? parseInt(value) : undefined)} value={field.value?.toString()}>
                        <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                          <SelectValue placeholder="Select graduation year" />
                        </SelectTrigger>
                        <SelectContent>
                          {Array.from({ length: new Date().getFullYear() + 5 - 1970 + 1 }, (_, i) => {
                            const year = new Date().getFullYear() + 5 - i;
                            return (
                              <SelectItem key={year} value={year.toString()}>
                                {year}
                              </SelectItem>
                            );
                          })}
                        </SelectContent>
                      </Select>
                    )}
                  />
                  {errors.education?.[index]?.graduation_year && (
                    <p className="text-red-400 text-sm mt-1">{errors.education[index]?.graduation_year?.message}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Submit Buttons */}
      <div className="flex justify-center gap-4 pt-4">
        {isEditing && onCancel && (
          <Button
            type="button"
            onClick={onCancel}
            disabled={loading}
            size="lg"
            variant="outline"
            className="border-red-500 text-red-400 hover:bg-red-500 hover:text-white bg-transparent px-12 py-3 text-lg font-semibold"
          >
            Cancel
          </Button>
        )}
        <Button
          type="submit"
          disabled={loading}
          size="lg"
          className="bg-green-600 hover:bg-green-700 disabled:opacity-50 px-12 py-3 text-lg font-semibold"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              {isEditing ? 'Updating Your Profile...' : 'Creating Your Interactive Resume...'}
            </>
          ) : (
            isEditing ? 'Update Profile' : 'Generate My MCP URL'
          )}
        </Button>
      </div>
    </form>
  )
}