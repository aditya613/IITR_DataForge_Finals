import axios from 'axios'

const API_BASE = '/api'

export interface LLMConfig {
  provider: string
  api_key: string
  model: string
  base_url: string
}

export interface AnalysisRequest {
  source_db_path: string
  target_db_path: string
  threshold: number
  llm_config?: LLMConfig
}

export interface ColumnMapping {
  source_column: string
  target_column: string
  source_table: string
  target_table: string
  bert_score: number
  llm_score: number
  tfidf_score: number
  domain_score: number
  ensemble_score: number
  confidence_level: string
  llm_reasoning: string
}

export interface AnalysisResult {
  status: string
  source_tables: number
  target_tables: number
  total_mappings: number
  statistics: {
    high_confidence: number
    medium_confidence: number
    low_confidence: number
    average_scores: {
      bert: number
      llm: number
      tfidf: number
      domain: number
    }
  }
  llm_enabled: boolean
  grouped_mappings: Record<string, ColumnMapping[]>
  all_mappings: ColumnMapping[]
}

export interface ValidationResult {
  status: string
  summary: {
    passed: number
    failed: number
    warnings: number
    total: number
  }
  results: Array<{
    check_name: string
    status: string
    severity: string
    message: string
    details: Record<string, any>
    recommendations: string[]
  }>
}

export interface MigrationResult {
  status: string
  summary: {
    total_migrated: number
    total_failed: number
    success_rate: number
  }
  table_results: Array<{
    source_table: string
    target_table: string
    records_migrated: number
    records_failed: number
  }>
  failed_records: Array<{
    record_id: string
    error_message: string
    original_data: Record<string, any>
  }>
}

export interface SchemaInfo {
  database: string
  tables: Array<{
    name: string
    row_count: number
    columns: Array<{
      name: string
      type: string
      nullable: boolean
      is_primary_key: boolean
      is_foreign_key: boolean
      sample_values: any[]
    }>
  }>
}

// API Functions

export async function checkHealth() {
  const response = await axios.get(`${API_BASE.replace('/api', '')}/health`)
  return response.data
}

export async function checkSampleData() {
  const response = await axios.get(`${API_BASE}/sample-data/status`)
  return response.data
}

export async function createSampleData() {
  const response = await axios.post(`${API_BASE}/sample-data/create`)
  return response.data
}

export async function extractSchema(dbPath: string): Promise<SchemaInfo> {
  const response = await axios.post(`${API_BASE}/schema/extract`, null, {
    params: { db_path: dbPath }
  })
  return response.data
}

export async function runAnalysis(request: AnalysisRequest): Promise<AnalysisResult> {
  const response = await axios.post(`${API_BASE}/match/analyze`, request)
  return response.data
}

export async function runValidation(sourcePath: string, targetPath: string): Promise<ValidationResult> {
  const response = await axios.post(`${API_BASE}/validate`, null, {
    params: { source_path: sourcePath, target_path: targetPath }
  })
  return response.data
}

export async function executeMigration(
  sourcePath: string,
  targetPath: string,
  mappings: ColumnMapping[],
  batchSize: number = 100
): Promise<MigrationResult> {
  const response = await axios.post(`${API_BASE}/migrate/execute`, {
    source_db_path: sourcePath,
    target_db_path: targetPath,
    mappings: mappings,
    batch_size: batchSize,
    use_transaction: true
  })
  return response.data
}

export async function uploadDatabase(file: File): Promise<{ file_path: string; filename: string }> {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await axios.post(`${API_BASE}/upload/database`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export async function getSankeyData(mappings: ColumnMapping[]) {
  const response = await axios.post(`${API_BASE}/visualizations/sankey`, mappings)
  return response.data
}
