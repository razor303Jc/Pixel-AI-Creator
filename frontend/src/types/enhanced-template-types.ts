// Enhanced Template Creation with Tiered Pricing and Security Features
// This specification outlines the implementation of optional tools with pricing tiers,
// enterprise integrations, social media analysis, and compliance features

interface BaseTemplateTools {
  id: string;
  name: string;
  description: string;
  isEnabled: boolean;
}

export interface ToolPricingTier {
  tier: 'free' | 'premium' | 'enterprise';
  monthlyPrice: number;
  paymentModel: 'subscription' | 'pay-per-use' | 'credits';
  usageLimits?: {
    requestsPerMonth?: number;
    storageGB?: number;
    apiCallsPerDay?: number;
  };
}

export interface EnhancedTemplateTools extends BaseTemplateTools {
  id: string;
  name: string;
  type: 'mcp-server' | 'api' | 'database' | 'workspace-integration' | 'social-media' | 'analytics' | 'ai-analysis';
  description: string;
  pricingTier: ToolPricingTier;
  isOptional: boolean;
  requiresVerification?: boolean;
  complianceLevel: 'basic' | 'gdpr' | 'hipaa' | 'enterprise';
  configuration: {
    endpoint?: string;
    capabilities?: string[];
    authentication?: {
      type: 'oauth2' | 'api-key' | 'mcp-auth' | 'enterprise-sso';
      provider?: 'google' | 'microsoft' | 'custom';
      scopes?: string[];
      encryptionLevel: 'standard' | 'enterprise' | 'zero-trust';
    };
    dataRetention?: {
      days: number;
      location: 'us' | 'eu' | 'user-choice';
      encryption: boolean;
    };
  };
  isEnabled: boolean;
  userConsent?: {
    termsAccepted: boolean;
    privacyPolicyAccepted: boolean;
    dataProcessingConsent: boolean;
    timestamp: string;
  };
}

export interface SocialMediaAnalysis {
  platforms: {
    website?: {
      url: string;
      analysisDepth: 'basic' | 'comprehensive' | 'ai-enhanced';
      crawlFrequency: 'daily' | 'weekly' | 'on-demand';
      contentTypes: ('text' | 'images' | 'videos' | 'metadata')[];
    };
    socialMedia?: {
      platform: 'linkedin' | 'twitter' | 'facebook' | 'instagram' | 'youtube' | 'tiktok';
      handle: string;
      analysisType: 'public-only' | 'authenticated' | 'deep-insights';
      pricingTier: ToolPricingTier;
    }[];
  };
  aiContextGeneration: {
    enabled: boolean;
    analysisTypes: ('brand-voice' | 'content-style' | 'audience-insights' | 'trend-analysis')[];
    updateFrequency: 'real-time' | 'daily' | 'weekly';
    pricingTier: ToolPricingTier;
  };
}

export interface WorkspaceIntegration {
  googleWorkspace?: {
    enabled: boolean;
    services: {
      gmail: { enabled: boolean; scope: string[]; pricingTier: ToolPricingTier };
      calendar: { enabled: boolean; scope: string[]; pricingTier: ToolPricingTier };
      drive: { enabled: boolean; scope: string[]; pricingTier: ToolPricingTier };
      docs: { enabled: boolean; scope: string[]; pricingTier: ToolPricingTier };
      sheets: { enabled: boolean; scope: string[]; pricingTier: ToolPricingTier };
      meet: { enabled: boolean; scope: string[]; pricingTier: ToolPricingTier };
    };
    enterpriseFeatures?: {
      adminSDK: boolean;
      auditLogs: boolean;
      dlp: boolean; // Data Loss Prevention
      vault: boolean;
    };
  };
  microsoft365?: {
    enabled: boolean;
    services: {
      outlook: { enabled: boolean; scope: string[]; pricingTier: ToolPricingTier };
      calendar: { enabled: boolean; scope: string[]; pricingTier: ToolPricingTier };
      oneDrive: { enabled: boolean; scope: string[]; pricingTier: ToolPricingTier };
      word: { enabled: boolean; scope: string[]; pricingTier: ToolPricingTier };
      excel: { enabled: boolean; scope: string[]; pricingTier: ToolPricingTier };
      teams: { enabled: boolean; scope: string[]; pricingTier: ToolPricingTier };
      sharepoint: { enabled: boolean; scope: string[]; pricingTier: ToolPricingTier };
    };
    enterpriseFeatures?: {
      azureAD: boolean;
      complianceCenter: boolean;
      informationProtection: boolean;
      advancedThreatProtection: boolean;
    };
  };
}

export interface SecurityCompliance {
  dataProtection: {
    encryption: {
      inTransit: boolean;
      atRest: boolean;
      keyManagement: 'managed' | 'customer-managed' | 'hsm';
    };
    dataResidency: {
      region: string;
      crossBorderRestrictions: boolean;
      localStorageRequired: boolean;
    };
    retention: {
      defaultDays: number;
      userConfigurable: boolean;
      automaticDeletion: boolean;
    };
  };
  compliance: {
    gdpr: {
      enabled: boolean;
      dataProcessingBasis: string;
      rightToErasure: boolean;
      dataPortability: boolean;
    };
    ccpa: {
      enabled: boolean;
      doNotSell: boolean;
      dataTransparency: boolean;
    };
    hipaa: {
      enabled: boolean;
      baa: boolean; // Business Associate Agreement
      auditLogs: boolean;
    };
    sox: {
      enabled: boolean;
      financialDataControls: boolean;
    };
  };
  audit: {
    enabled: boolean;
    logRetentionDays: number;
    realTimeMonitoring: boolean;
    anomalyDetection: boolean;
  };
}

export interface UserConsent {
  registration: {
    termsOfService: {
      version: string;
      acceptedAt: string;
      ipAddress: string;
      userAgent: string;
    };
    privacyPolicy: {
      version: string;
      acceptedAt: string;
      dataProcessingConsent: boolean;
      marketingConsent: boolean;
      analyticsConsent: boolean;
    };
    cookieConsent: {
      necessary: boolean;
      functional: boolean;
      analytics: boolean;
      marketing: boolean;
      acceptedAt: string;
    };
  };
  toolSpecific: {
    [toolId: string]: {
      dataAccess: boolean;
      dataProcessing: boolean;
      thirdPartySharing: boolean;
      acceptedAt: string;
    };
  };
}

export interface EnhancedTemplateForm {
  // Basic Information
  basicInfo: {
    name: string;
    description: string;
    category: string;
    personality: string;
    tags: string[];
    visibility: 'private' | 'public' | 'team' | 'enterprise';
    pricingTier: 'free' | 'premium' | 'enterprise';
  };

  // Instructions and Training
  instructions: string;
  scope: 'general' | 'specialized' | 'expert' | 'domain-specific';
  trainingQA: Array<{ question: string; answer: string }>;

  // Optional Tools (Tiered Pricing)
  tools: {
    // Free Tier
    basicChat: { enabled: boolean };
    textGeneration: { enabled: boolean };
    basicAnalytics: { enabled: boolean };

    // Premium Tier (Subscription/Pay-per-use)
    mcpServers: {
      enabled: boolean;
      servers: EnhancedTemplateTools[];
      pricingModel: 'subscription' | 'pay-per-use';
    };
    databaseAccess: {
      enabled: boolean;
      types: ('postgresql' | 'mysql' | 'mongodb' | 'redis')[];
      pricingModel: 'subscription' | 'pay-per-query';
    };
    apiIntegrations: {
      enabled: boolean;
      apis: EnhancedTemplateTools[];
      pricingModel: 'subscription' | 'pay-per-call';
    };

    // Enterprise Tier
    workspaceIntegrations: WorkspaceIntegration;
    socialMediaAnalysis: SocialMediaAnalysis;
    advancedAnalytics: {
      enabled: boolean;
      features: ('sentiment-analysis' | 'trend-detection' | 'predictive-analytics')[];
    };
  };

  // Security and Compliance
  security: SecurityCompliance;
  userConsent: UserConsent;

  // Context Enhancement
  contextSources: {
    websiteAnalysis: {
      enabled: boolean;
      urls: string[];
      analysisDepth: 'basic' | 'comprehensive' | 'ai-enhanced';
      updateFrequency: 'manual' | 'daily' | 'real-time';
    };
    socialMediaAnalysis: SocialMediaAnalysis;
    documentLibrary: {
      enabled: boolean;
      sources: ('google-drive' | 'onedrive' | 'dropbox' | 'local-upload')[];
    };
  };
}

// Pricing Tiers Definition
export const PRICING_TIERS = {
  free: {
    tier: 'free',
    monthlyPrice: 0,
    paymentModel: 'subscription',
    usageLimits: {
      requestsPerMonth: 1000,
      storageGB: 1,
      apiCallsPerDay: 100
    },
    features: ['Basic Chat', 'Text Generation', 'Simple Analytics']
  },
  premium: {
    tier: 'premium',
    monthlyPrice: 29,
    paymentModel: 'subscription',
    usageLimits: {
      requestsPerMonth: 10000,
      storageGB: 10,
      apiCallsPerDay: 1000
    },
    features: ['MCP Servers', 'Database Access', 'API Integrations', 'Google Workspace Basic']
  },
  enterprise: {
    tier: 'enterprise',
    monthlyPrice: 299,
    paymentModel: 'subscription',
    usageLimits: {
      requestsPerMonth: -1, // Unlimited
      storageGB: 100,
      apiCallsPerDay: 10000
    },
    features: ['Full Google Workspace', 'Microsoft 365', 'Social Media Analysis', 'Advanced Analytics', 'Custom Compliance']
  }
} as const;