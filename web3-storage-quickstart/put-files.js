import process from 'process'
import minimist from 'minimist'
import { Web3Storage, getFilesFromPath } from 'web3.storage'

async function store_data (fileName) {
  const args = minimist(process.argv.slice(2))
  //const token = args.token
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweEM2OUZhOUJkQjRmRjdlNzYwMzlDOTE5M0U3MmQ1QjFBMjEzNTQ3MzAiLCJpc3MiOiJ3ZWIzLXN0b3JhZ2UiLCJpYXQiOjE2OTE0OTU5MzI5MDcsIm5hbWUiOiJGTCJ9.ZBYyTLByu6TxlJuL7pWwdEJzb3wWxcVhTeD9aIC2x5A'
  //const path = './web3-storage-quickstart/' + client + '.txt'
  const path = './web3-storage-quickstart/'+ fileName +''
  //const path = './'+ fileName +''
  if (!token) {
    return console.error('A token is needed. You can create one on https://web3.storage')
  }

  /*if (args._.length < 1) {
    return console.error('Please supply the path to a file or directory')
  }*/

  const storage = new Web3Storage({ token })
  const files = []
  const pathFiles = await getFilesFromPath(path)
  files.push(...pathFiles)
  /*for (const path of args._) {
    const pathFiles = await getFilesFromPath(path)
    files.push(...pathFiles)
  }*/

  //console.log(`Uploading ${files.length} files`)
  const cid = await storage.put(files)
  console.log(cid)
  //console.log(cid)
}

const args = process.argv.slice(2);
store_data(JSON.parse(args[0]));
//store_data("clients_model");