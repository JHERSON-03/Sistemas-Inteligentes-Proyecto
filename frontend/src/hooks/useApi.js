import { useCallback, useEffect, useState } from 'react'

/** Carga datos de la API con estados de carga y error. */
export function useApi(fetcher, deps = []) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const load = useCallback(fetcher, deps)

  const reload = useCallback(() => {
    setLoading(true)
    setError(null)
    return load()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [load])

  useEffect(() => { reload() }, [reload])

  return { data, setData, error, loading, reload }
}
