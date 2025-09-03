import { Button } from "@/components/ui/button"

export function TestComponent() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4">
      <h1 className="text-2xl font-bold">Shadcn UI Test</h1>
      <p className="text-muted-foreground">If you can see this styled text, Tailwind CSS is working!</p>
      
      <div className="flex gap-2">
        <Button>Default Button</Button>
        <Button variant="outline">Outline Button</Button>
        <Button variant="secondary">Secondary Button</Button>
      </div>
      
      <p className="text-sm text-muted-foreground">
        If the buttons above are styled correctly, shadcn UI is working!
      </p>
    </div>
  )
}