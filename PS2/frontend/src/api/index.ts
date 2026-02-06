import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' }
})

export interface UploadResponse {
  session_id: string
  source_tables: string[]
  target_tables: string[]
  source_columns: number
  target_columns: number
}

export interface AnalysisResponse {
  session_id: string
  total_mappings: number
  statistics: {
    total_mappings: number
    high_confidence: number
    medium_confidence: number
    low_confidence: number
    average_score: number
    gemini_enabled: boolean
    bert_enabled: boolean
  }
  unmapped_source: number
  unmapped_target: number
  gemini_used: boolean
}

export interface MappingReport {
  session_id: string
  generated_at: string
  mappings: Array<{
    source_table: string
    source_column: string
    source_type: string
    target_table: string
    target_column: string
    target_type: string
    confidence_score: number
    confidence_level: string
    mapping_type: string
    transformation: string
    scores: {
      bert: number
      gemini: number
      tfidf: number
      domain: number
    }
    explainability: {
      why_mapped: string
      why_not_others: string
      summary: string
    }
  }>
  unmapped_source_columns: Array<{ table: string; column: string; reason: string }>
  unmapped_target_columns: Array<{ table: string; column: string; reason: string }>
  statistics: Record<string, unknown>
}

export interface ValidationReport {
  session_id: string
  generated_at: string
  row_comparison: Record<string, { source: number; target: number; difference: number; match: boolean }>
  null_checks: Record<string, { source_nulls: number; target_nulls: number; match: boolean }>
  duplicate_checks: Record<string, { has_duplicates: boolean; duplicate_count: number }>
  referential_integrity: Array<unknown>
  failed_records: Array<{ source_table: string; target_table: string; data: Record<string, unknown>; error: string; reason: string }>
  is_valid: boolean
  summary: string
  migration_stats: { rows_migrated: number; rows_failed: number }
}

export interface VisualizationData {
  session_id: string
  sankey: {
    nodes: Array<{ id: string; name: string; type: string; table: string; reason?: string }>
    links: Array<{ source: number; target: number; value: number; confidence: string; mapping_type: string; explanation: string }>
  }
  table_mappings: Array<{
    source_table: string
    target_table: string
    columns: Array<{ source: string; target: string; confidence: string; score: number }>
  }>
  summary: {
    total_mappings: number
    high_confidence: number
    medium_confidence: number
    low_confidence: number
    unmapped_source: number
    unmapped_target: number
  }
}

export interface ExplainabilityReport {
  column_mappings: Array<{
    question: string
    answer: string
    confidence: string
    details: Record<string, string>
  }>
  ignored_columns: Array<{ question: string; answer: string }>
  transformations: Array<{ question: string; answer: string; source_type: string; target_type: string }>
  failed_data: Array<{ question: string; record: Record<string, unknown>; error: string; reason: string }>
  summary: string
}

// API Functions
export const uploadDatabases = async (sourceFile: File, targetFile: File): Promise<UploadResponse> => {
  const formData = new FormData()
  formData.append('source_db', sourceFile)
  formData.append('target_db', targetFile)
  const { data } = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export const analyzeSchemas = async (sessionId: string, threshold: number = 0.6): Promise<AnalysisResponse> => {
  const { data } = await api.post('/analyze', { session_id: sessionId, threshold })
  return data
}

export const getMappingReport = async (sessionId: string): Promise<MappingReport> => {
  const { data } = await api.get(`/mapping-report/${sessionId}`)
  return data
}

export const executeMigration = async (sessionId: string) => {
  const formData = new FormData()
  formData.append('session_id', sessionId)
  const { data } = await api.post('/migrate', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export const getValidationReport = async (sessionId: string): Promise<ValidationReport> => {
  const { data } = await api.get(`/validation-report/${sessionId}`)
  return data
}

export const getVisualizationData = async (sessionId: string): Promise<VisualizationData> => {
  const { data } = await api.get(`/visualization/${sessionId}`)
  return data
}

export const getExplainabilityReport = async (sessionId: string): Promise<ExplainabilityReport> => {
  const { data } = await api.get(`/explain/${sessionId}`)
  return data
}

export const createSampleData = async () => {
  const { data } = await api.get('/sample-data')
  return data
}

export const checkApiStatus = async () => {
  const { data } = await api.get('/')
  return data
}
