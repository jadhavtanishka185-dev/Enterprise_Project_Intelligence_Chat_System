import React from 'react'
import { FileText, File, FileType, Calendar, Layers } from 'lucide-react'
import { format } from 'date-fns'

const FILE_ICONS = {
  pdf: { icon: FileText, color: 'text-red-400', bg: 'bg-red-400/10' },
  docx: { icon: File, color: 'text-blue-400', bg: 'bg-blue-400/10' },
  doc: { icon: File, color: 'text-blue-400', bg: 'bg-blue-400/10' },
  txt: { icon: FileType, color: 'text-green-400', bg: 'bg-green-400/10' },
}

function formatSize(bytes) {
  if (!bytes) return 'Unknown size'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function DocumentList({ documents }) {
  if (!documents.length) {
    return (
      <div className="text-center py-12 text-gray-500">
        <FileText className="h-10 w-10 mx-auto mb-3 opacity-30" />
        <p className="text-sm">No documents uploaded yet</p>
        <p className="text-xs mt-1">Upload a PDF, DOCX, or TXT file to get started</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => {
        const typeInfo = FILE_ICONS[doc.file_type] || FILE_ICONS.txt
        const Icon = typeInfo.icon
        return (
          <div
            key={doc.id}
            className="flex items-center gap-4 p-4 bg-gray-800/50 border border-gray-700/50 rounded-xl hover:border-gray-600 transition-colors"
          >
            <div className={`w-10 h-10 ${typeInfo.bg} rounded-lg flex items-center justify-center flex-shrink-0`}>
              <Icon className={`h-5 w-5 ${typeInfo.color}`} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-200 truncate">{doc.filename}</p>
              <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-500">
                <span className="uppercase font-medium text-gray-600">{doc.file_type}</span>
                <span>{formatSize(doc.file_size)}</span>
                <div className="flex items-center gap-1">
                  <Layers className="h-3 w-3" />
                  <span>{doc.chunk_count} chunks</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1 text-xs text-gray-600 flex-shrink-0">
              <Calendar className="h-3 w-3" />
              <span>{format(new Date(doc.uploaded_at), 'MMM d')}</span>
            </div>
          </div>
        )
      })}
    </div>
  )
}
