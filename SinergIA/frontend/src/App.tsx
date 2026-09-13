import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { AuthorDetailPage } from './pages/AuthorDetailPage'
import { AuthorsPage } from './pages/AuthorsPage'
import { HomePage } from './pages/HomePage'
import { InstitutionDetailPage } from './pages/InstitutionDetailPage'
import { InstitutionsPage } from './pages/InstitutionsPage'
import { TopicsPage } from './pages/TopicsPage'
import { WorkDetailPage } from './pages/WorkDetailPage'
import { WorksPage } from './pages/WorksPage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="authors" element={<AuthorsPage />} />
        <Route path="authors/:authorId" element={<AuthorDetailPage />} />
        <Route path="works" element={<WorksPage />} />
        <Route path="works/:workId" element={<WorkDetailPage />} />
        <Route path="institutions" element={<InstitutionsPage />} />
        <Route path="institutions/:institutionId" element={<InstitutionDetailPage />} />
        <Route path="topics" element={<TopicsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
