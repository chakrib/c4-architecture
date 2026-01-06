/**
 * C4 Architecture Solution Overview Validator
 * 
 * Validates whether a technical solution overview contains sufficient
 * information to generate C4 Level 1 (System Context) and Level 2 (Container) diagrams.
 */

export const ValidationLevel = {
  ERROR: 'ERROR',     // Must fix - cannot generate C4 diagrams
  WARNING: 'WARNING', // Should fix - diagrams may be incomplete
  INFO: 'INFO'        // Optional - would improve diagram quality
}

export class ValidationResult {
  constructor(level, category, message, suggestion = '') {
    this.level = level
    this.category = category
    this.message = message
    this.suggestion = suggestion
  }
}

export class C4ValidationReport {
  constructor() {
    this.isValid = true
    this.errors = []
    this.warnings = []
    this.info = []
    this.score = 0
    this.refactoringSuggestion = ''
  }

  addResult(result) {
    if (result.level === ValidationLevel.ERROR) {
      this.errors.push(result)
    } else if (result.level === ValidationLevel.WARNING) {
      this.warnings.push(result)
    } else {
      this.info.push(result)
    }
  }

  getSummary() {
    const status = this.isValid ? '✓ VALID' : '✗ INVALID'
    return `${status} - C4 Diagram Generation Readiness: ${this.score.toFixed(1)}/100
Errors: ${this.errors.length}
Warnings: ${this.warnings.length}
Info: ${this.info.length}`
  }

  getFormattedReport() {
    let report = this.getSummary() + '\n\n'

    if (this.errors.length > 0) {
      report += '🔴 ERRORS (Must Fix):\n'
      this.errors.forEach((error, i) => {
        report += `\n${i + 1}. [${error.category}]\n`
        report += `   ${error.message}\n`
        if (error.suggestion) {
          report += `   💡 ${error.suggestion}\n`
        }
      })
    }

    if (this.warnings.length > 0) {
      report += '\n🟡 WARNINGS (Should Fix):\n'
      this.warnings.forEach((warning, i) => {
        report += `\n${i + 1}. [${warning.category}]\n`
        report += `   ${warning.message}\n`
        if (warning.suggestion) {
          report += `   💡 ${warning.suggestion}\n`
        }
      })
    }

    if (this.info.length > 0) {
      report += '\n🔵 INFORMATION (Optional):\n'
      this.info.forEach((info, i) => {
        report += `\n${i + 1}. [${info.category}]\n`
        report += `   ${info.message}\n`
        if (info.suggestion) {
          report += `   💡 ${info.suggestion}\n`
        }
      })
    }

    return report
  }
}

export class C4SolutionValidator {
  constructor() {
    // Keywords that indicate system components
    this.SYSTEM_KEYWORDS = ['system', 'application', 'service', 'platform', 'portal',
      'api', 'backend', 'frontend', 'database', 'server']

    // Keywords that indicate users/actors
    this.USER_KEYWORDS = ['user', 'customer', 'admin', 'operator', 'client',
      'employee', 'developer', 'manager', 'actor', 'role']

    // Keywords that indicate containers
    this.CONTAINER_KEYWORDS = ['web application', 'mobile app', 'api', 'database', 'cache',
      'message queue', 'microservice', 'lambda', 'function',
      'container', 'service', 'storage', 'file system']

    // Keywords that indicate external systems
    this.EXTERNAL_KEYWORDS = ['third-party', 'external', 'integration', 'saas', 'cloud service',
      'payment gateway', 'authentication service', 'email service']

    // Keywords that indicate relationships/interactions
    this.RELATIONSHIP_KEYWORDS = ['connect', 'communicate', 'interact', 'send', 'receive',
      'call', 'request', 'response', 'publish', 'subscribe',
      'read', 'write', 'query', 'update', 'integrate', 'access', 'manage', 'share']
  }

  validate(text) {
    const report = new C4ValidationReport()

    if (!text || !text.trim()) {
      report.addResult(new ValidationResult(
        ValidationLevel.ERROR,
        'Input',
        'Empty input provided',
        'Please describe what you want to build'
      ))
      report.isValid = false
      return report
    }

    // Check minimum length
    const wordCount = text.split(/\s+/).length
    if (wordCount < 3) {
      report.addResult(new ValidationResult(
        ValidationLevel.ERROR,
        'Content Length',
        'Input too short',
        'Please provide at least a brief description'
      ))
      report.isValid = false
      return report
    }

    const textLower = text.toLowerCase()

    // For C4 Level 1, we need to identify:
    // 1. The System (what are we building?)
    // 2. Users/Actors (who uses it?)
    // 3. External Systems (optional - what does it connect to?)

    const analysis = this._analyzeForC4Requirements(textLower)

    // If we can't identify the system, ask for clarification
    if (!analysis.hasSystem) {
      report.addResult(new ValidationResult(
        ValidationLevel.ERROR,
        'System Not Identified',
        'Cannot identify what system/application you want to build',
        'Please specify what you want to create (e.g., "web app", "mobile app", "system", "service")'
      ))
      report.isValid = false
    }

    // If no users mentioned, ask (but don't block)
    if (!analysis.hasUsers && analysis.hasSystem) {
      report.addResult(new ValidationResult(
        ValidationLevel.WARNING,
        'Users Not Specified',
        'Who will use this system?',
        'Consider adding: "Users access...", "Customers use...", "Admins manage...", etc.'
      ))
    }

    // Calculate score
    report.score = this._calculateScore(report)

    // Valid if we can at least identify the system
    report.isValid = report.errors.length === 0

    return report
  }

  _analyzeForC4Requirements(textLower) {
    // Check if we can identify a system
    const systemIndicators = [
      'build', 'create', 'develop', 'make', 'design',
      'system', 'application', 'app', 'service', 'platform', 'tool',
      'web', 'mobile', 'api', 'backend', 'frontend', 'dashboard',
      'website', 'portal', 'interface'
    ]

    const hasSystem = systemIndicators.some(indicator => 
      textLower.includes(indicator)
    )

    // Check if users/actors are mentioned
    const userIndicators = [
      'user', 'users', 'customer', 'customers', 'admin', 'administrator',
      'client', 'clients', 'people', 'person', 'employee', 'staff',
      'developer', 'manager', 'operator', 'visitor', 'member'
    ]

    const hasUsers = userIndicators.some(indicator => 
      textLower.includes(indicator)
    )

    // Check if external systems are mentioned
    const externalIndicators = [
      'api', 'database', 'server', 'service', 'integration',
      'whatsapp', 'google', 'aws', 'azure', 'stripe', 'paypal',
      'email', 'sms', 'storage', 's3', 'sftp', 'ftp'
    ]

    const hasExternalSystems = externalIndicators.some(indicator => 
      textLower.includes(indicator)
    )

    return {
      hasSystem,
      hasUsers,
      hasExternalSystems
    }
  }

  _isGibberish(text) {
    // Check for repeated characters (like "asdasdasd")
    const repeatedPattern = /(.{2,})\1{3,}/
    if (repeatedPattern.test(text)) {
      return true
    }

    // Check for excessive consonants without vowels
    const words = text.toLowerCase().split(/\s+/)
    let gibberishWordCount = 0
    let totalMeaningfulWords = 0
    
    for (const word of words) {
      if (word.length < 3) continue // Skip short words
      
      totalMeaningfulWords++
      
      // Count vowels
      const vowelCount = (word.match(/[aeiou]/g) || []).length
      const consonantCount = (word.match(/[bcdfghjklmnpqrstvwxyz]/g) || []).length
      
      // If word has many consonants but very few vowels, likely gibberish
      if (word.length > 5 && vowelCount < 2) {
        gibberishWordCount++
      }
      
      // Check for random character sequences (more than 4 consonants in a row)
      if (/[bcdfghjklmnpqrstvwxyz]{5,}/.test(word)) {
        gibberishWordCount++
      }
    }
    
    // If more than 20% of words are gibberish, reject
    if (totalMeaningfulWords > 0 && gibberishWordCount / totalMeaningfulWords > 0.2) {
      return true
    }

    // Check if text contains mostly random characters
    const alphaCount = (text.match(/[a-zA-Z]/g) || []).length
    const totalChars = text.replace(/\s/g, '').length
    
    // If less than 80% alphabetic characters, might be gibberish
    if (totalChars > 0 && alphaCount / totalChars < 0.8) {
      return true
    }

    // Check for very long words without spaces (keyboard mashing)
    const hasLongGibberish = /[a-z]{20,}/.test(text.toLowerCase())
    if (hasLongGibberish) {
      return true
    }

    // Check for common English words - need a minimum percentage
    const commonWords = [
      'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
      'build', 'create', 'make', 'develop', 'system', 'app', 'application', 'web', 'mobile',
      'data', 'user', 'users', 'from', 'that', 'this', 'is', 'are', 'will', 'can', 'need',
      'want', 'have', 'has', 'use', 'using', 'connect', 'integrate', 'send', 'receive',
      'service', 'api', 'database', 'server', 'client', 'platform', 'interface'
    ]
    
    let commonWordCount = 0
    for (const word of commonWords) {
      const regex = new RegExp(`\\b${word}\\b`, 'gi')
      const matches = text.match(regex)
      if (matches) {
        commonWordCount += matches.length
      }
    }
    
    // Need at least 3 common words OR 15% of total words to be common
    const totalWords = words.length
    if (totalWords > 10 && commonWordCount < 3) {
      return true
    }
    
    if (totalWords > 5 && commonWordCount / totalWords < 0.15) {
      return true
    }

    return false
  }

  _checkMinimumLength(text, report) {
    // Removed - handled in main validate method
  }

  _checkSystemIdentification(textLower, report) {
    // Removed - handled in _analyzeForC4Requirements
  }

  _checkUserActors(textLower, report) {
    // Don't check for users - it's optional
  }

  _checkContainers(textLower, report) {
    // Don't require specific components - let AI figure it out
  }

  _checkExternalSystems(textLower, report) {
    // Don't require external systems - optional
  }

  _checkRelationships(textLower, report) {
    // Don't require explicit relationships - AI can infer
  }

  _checkTechnologyStack(text, report) {
    // Don't require specific technologies - optional
  }

  _calculateScore(report) {
    let score = 100.0
    score -= report.errors.length * 25
    score -= report.warnings.length * 10
    score -= report.info.length * 2
    return Math.max(0.0, score)
  }
}
