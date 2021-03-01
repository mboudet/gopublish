import React, { Component } from 'react'
import axios from 'axios'
import { Badge } from 'reactstrap'
import FileDownload from 'js-file-download'
import update from 'react-addons-update'
import { withRouter } from "react-router-dom";
import PropTypes from 'prop-types'
import Utils from '../classes/utils'
import { Redirect } from 'react-router-dom'

import Home from './home'

class File extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
    this.state = {
      isLoading: true,
      file: {},
      email: ""
    }
    this.downloadFile = this.downloadFile.bind(this)
    this.pullFile = this.pullFile.bind(this)
    this.handleChangeEmail = this.handleChangeEmail.bind(this)
    this.cancelRequest
  }

  downloadFile(event){
    let uri = this.props.match.params.uri;
    let requestUrl = '/api/data/download/' + uri;
    let data = { fileId: event.target.id }
    axios.get(requestUrl, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then((response) => {
        FileDownload(response.data, this.state.file.file_name)
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
        })
      })
  }

  pullFile(event){
    let uri = this.props.match.params.uri;
    let requestUrl = '/api/data/download/' + uri;
    let data = {email: this.state.email}
    axios.post(requestUrl, {baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then((response) => {
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
        })
      })
      .catch(error => {
        console.log(error, error.response.data.errorMessage)
        this.setState({
          error: true,
          errorMessage: error.response.data.errorMessage,
          status: error.response.status,
        })
      })
  }

  handleChangeEmail (event) {
    this.setState({
      email: event.target.value
    })
  }

  validateEmail () {
    let email = this.state.email
    if (email == ""){
      return true
    } else {
      let re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      return re.test(String(email).toLowerCase())
    }
  }

  componentDidMount () {
    this.loadFile()
  }

  loadFile() {
    let uri = this.props.match.params.uri;
    let requestUrl = '/api/view/' + uri
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        console.log("test2")
        this.setState({
          isLoading: false,
          file: response.data.file,
        })
      })
      .catch(error => {
        console.log(error.response)
        this.setState({
            error: true,
            errorCode: error.response.status,
            errorMessage: error.response.statusText,
        })
      })
  }

  componentWillUnmount () {
    this.cancelRequest()
  }

  render () {
    if (this.state.error) {
        return (
            <div className="container">
            <h2>Error <i>{this.state.errorCode}</i> fetching file: <i>{this.state.errorMessage}</i></h2>
            </div>
        )
    }
    

    let uri = this.props.match.params.uri;
    let file = this.state.file
    let contact = ""
    let status = ""
    let form = ""
    let action = ""

    if (file.contact){
      contact = <p>Contact: {file.contact}</p>
    } else {
      contact = <p>Owner: {file.owner}</p>
    }

    status = <p></p>
    if (file.status == "available"){
      status = <p>Status: <Badge color="success">Available</Badge></p>
      '<Button size="sm" outline color="success" onClick={this.downloadFile}>Download file</Button>'
    }
    if (file.status == "unavailable" || file.status == "failed"){
      status = <p>Status: <Badge color="danger">Unavailable</Badge></p>
    }
    if (file.status == "pulling"){
      status = <p>Status: <Badge color="secondary">Pulling</Badge></p>
    }
    if (file.status == "pullable"){
      status = <p>Status: <Badge color="started">Pullable</Badge></p>
      action = '<Button size="sm" outline color="started" disabled={this.validateEmail()} onClick={this.pullFile}>Pull file</Button>'
      form = `<FormGroup>
                <Label for="email">Optional notification email</Label>
                <Input type="email" name="email" id="email" placeholder="Your email" value={this.state.email} onChange={this.handleChangeEmail} />
              </FormGroup>`
    }
    if (file.status == "starting" || file.status == "hashing"){
      status = <p>Status: <Badge color="warning">Publishing</Badge></p>
    }

    return (
      <div className="container">
        <h2>Information about file {file.file_name}, version {file.version}</h2>
        <br />
        {status}
        <p>File size: {this.utils.humanFileSize(file.size, true)}</p>
        {contact}
        <p>Publishing date: {file.publishing_date}</p>
        <p>File MD5: {file.hash}</p>
        <br />
        {form}
        {action}
      </div>
    )
  }
}

File.propTypes = {
  config: PropTypes.object,
  match: PropTypes.object
}

export default withRouter(File)
