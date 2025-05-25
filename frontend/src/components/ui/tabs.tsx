import * as React from "react"

interface TabsProps {
  value: string
  onValueChange: (value: string) => void
  className?: string
  children: React.ReactNode
}

export function Tabs({ value, onValueChange, className, children }: TabsProps) {
  return (
    <div className={className}>
      {React.Children.map(children, child => 
        React.isValidElement(child) 
          ? React.cloneElement(child as React.ReactElement<any>, { currentValue: value, onValueChange })
          : child
      )}
    </div>
  )
}

interface TabsListProps {
  className?: string
  children: React.ReactNode
  currentValue?: string
  onValueChange?: (value: string) => void
}

export function TabsList({ className, children, currentValue, onValueChange }: TabsListProps) {
  return (
    <div className={`inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground ${className || ''}`}>
      {React.Children.map(children, child => 
        React.isValidElement(child) 
          ? React.cloneElement(child as React.ReactElement<any>, { currentValue, onValueChange })
          : child
      )}
    </div>
  )
}

interface TabsTriggerProps {
  value: string
  children: React.ReactNode
  className?: string
  currentValue?: string
  onValueChange?: (value: string) => void
}

export function TabsTrigger({ value: triggerValue, children, className, currentValue, onValueChange }: TabsTriggerProps) {
  const isActive = currentValue === triggerValue
  
  return (
    <button
      className={`inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${
        isActive 
          ? 'bg-background text-foreground shadow-sm' 
          : 'hover:bg-background/50'
      } ${className || ''}`}
      onClick={() => onValueChange?.(triggerValue)}
    >
      {children}
    </button>
  )
}

interface TabsContentProps {
  value: string
  children: React.ReactNode
  className?: string
  currentValue?: string
}

export function TabsContent({ value: contentValue, children, className, currentValue }: TabsContentProps) {
  if (currentValue !== contentValue) return null
  
  return (
    <div className={`mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ${className || ''}`}>
      {children}
    </div>
  )
} 