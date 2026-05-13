import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function LoginPage() {
  const navigate = useNavigate()

  useEffect(() => {
    // Redirect to user login page
    navigate('/user/login', { replace: true })
  }, [navigate])

  return null
}
