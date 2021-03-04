import React, { Component } from 'react'
import axios from 'axios'
import { Badge, Button, Card, CardTitle, CardBody, CardText, Form, FormGroup, Input, Label} from 'reactstrap'
import update from 'react-addons-update'
import { withRouter } from "react-router-dom";
import PropTypes from 'prop-types'
import Utils from '../classes/utils'
import { Link, Redirect } from 'react-router-dom'

export default class Files extends Component {
  constructor (props) {
    super(props)
    this.state = {
      isLoading: true,
      files: [],
    }
    this.utils = new Utils()
  }


  componentDidMount () {
    this.listFiles()
  }

  listFiles() {
    let requestUrl = '/api/list'
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }) })
      .then(response => {
        this.setState({
          isLoading: false,
          files: response.data.files,
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

  render () {

    if (this.state.error) {
        return (
            <div className="container">
            <h2>Error <i>{this.state.errorCode}</i> fetching files: <i>{this.state.errorMessage}</i></h2>
            </div>
        )
    }

    if (this.state.files.length == 0) {
        return (
            <div className="container">
            <h2>No files available</h2>
            </div>
        )
    }

    const setStatus = (file_status) => {
        let status = <div></div>
        if (file_status == "available"){
            status = <Badge className="float-right" color="success">Available</Badge>
        }
        if (file_status == "unavailable" || file_status == "failed"){
            status = <Badge className="float-right" color="danger">Unavailable</Badge>
        }
        if (file_status == "pulling"){
            status = <Badge className="float-right" color="secondary">Pulling</Badge>
        }
        if (file_status == "pullable"){
            status = <Badge className="float-right" color="started">Pullable</Badge>
        }
        if (file_status == "starting" || file_status == "hashing"){
            status = <Badge className="float-right" color="warning">Publishing</Badge>
        }
        return status
    }

    let content = this.state.files.map((item, i) => (
        <div key={i}>
        <Card>
          <CardBody>
            <CardTitle tag="h3"><i className="fas fa-file"></i> File : <Link to={"/files/" + item.uri}>{item.file_name}</Link>{setStatus(item.status)}</CardTitle>
            <CardText>
            File version : {item.version}
            <br/>
            Size : {this.utils.humanFileSize(item.size, true)}
            <br/>
            Downloads : {item.downloads}
            </CardText>
          </CardBody>
        </Card>
        <br/>
        </div>
      ))

    return (
      <div className="container">
        <h2 className="text-center">{this.state.files.length} {this.state.files.length == 1 ? "file" : "files"} available</h2>
        <br/>
        {content}
      </div>
    )
  }
}

Files.propTypes = {
  config: PropTypes.object,
}

