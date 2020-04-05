import React from 'react';
import './App.css';
import { object } from 'prop-types';

const hostname = window && window.location && window.location.hostname;
const BASE_URL = hostname.includes('localhost') ? "http://localhost:5000" : ''
interface data {Source:string,Text:string,Confidence:string};

async function search(text:string){
  const result = await fetch( BASE_URL + "/api/search?text="+text);
  const output: data[] = await result.json();
  return output;
}

function App() {
  const [data,setData] = React.useState<data[]>([]);
  const [searchText,setSearchText] = React.useState("");
  const [loadingResults,setLoadingResults] = React.useState(false);
  async function runSearch(text:string){
    setLoadingResults(true);
    const result = await search(text);
    setLoadingResults(false);
    setData(result);
  }
  React.useEffect(() => {
    (async () => {
      runSearch("");
    })()
  },[]);
  return (
    <div className="App">
      <h1>Covid paper Search</h1>
      Thousands of covid19 researchers are publishing papers to help address coronavirus. Ask a qu
      <div className="cvd-searchbar">
        <input placeholder="enter text to search"
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}></input>
        <button onClick={() => runSearch(searchText)}>Search</button>
      </div>
      {loadingResults && <div>
        AI is running...
      </div>}
      <ResultTable data={data} />
    </div>
  );
}

function ResultTable({data}:{data:data[]}){
  return (
    <div className="cvd-resulttable">
      <thead>
        <tr style={{textAlign: "right"}}>
          <th>Search results</th>
          <th>Confidence</th>
          <th>source</th>
        </tr>
      </thead>
      <tbody>
        {data.map((rowdata) => (<tr>
          <td>{rowdata.Text}</td>
          <td>{rowdata.Confidence}</td>
          <td><a href={rowdata.Source} target="_blank">source</a></td>
        </tr>))}
      </tbody>
    </div>
  )

}
export default App;
