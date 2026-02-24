import React, {useState} from 'react'

export default function App(){
  const [code, setCode] = useState('print(input())')
  const [language, setLanguage] = useState('python')
  const [tests, setTests] = useState([{input:'hello', expected_output:'hello'}])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const run = async () => {
    setLoading(true)
    setResult(null)
    try{
      const res = await fetch('http://127.0.0.1:8000/execute', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({code, language, tests})
      })
      const data = await res.json()
      setResult({status: res.status, body: data})
    }catch(e){
      setResult({error: String(e)})
    }finally{setLoading(false)}
  }

  const updateTest = (i, field, v) => {
    const t = [...tests]
    t[i][field] = v
    setTests(t)
  }
  const addTest = () => setTests([...tests, {input:'', expected_output:''}])

  return (
    <div className="container">
      <h1>TestPortal — Runner</h1>
      <div className="row">
        <div className="col">
          <label>Language</label>
          <select value={language} onChange={e=>setLanguage(e.target.value)}>
            <option value="python">Python</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
          </select>

          <label>Code</label>
          <textarea value={code} onChange={e=>setCode(e.target.value)} rows={10} />

          <label>Tests</label>
          {tests.map((t,i)=> (
            <div key={i} className="test-row">
              <input placeholder="input" value={t.input} onChange={e=>updateTest(i,'input',e.target.value)} />
              <input placeholder="expected output" value={t.expected_output} onChange={e=>updateTest(i,'expected_output',e.target.value)} />
            </div>
          ))}
          <button onClick={addTest}>Add test</button>
          <div style={{marginTop:12}}>
            <button onClick={run} disabled={loading}>{loading? 'Running...':'Run'}</button>
          </div>
        </div>

        <div className="col">
          <h3>Result</h3>
          <pre>{result? JSON.stringify(result,null,2):'No result yet'}</pre>
        </div>
      </div>
    </div>
  )
}
