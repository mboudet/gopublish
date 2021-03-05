import React, { Component } from 'react'
import axios from 'axios'
import { Badge, Button, Card, CardDeck, CardTitle, CardBody, CardHeader, CardText, Col, Form, FormGroup, Input, Label} from 'reactstrap'
import update from 'react-addons-update'
import { withRouter } from "react-router-dom";
import PropTypes from 'prop-types'
import Utils from '../classes/utils'
import { Link, Redirect } from 'react-router-dom'
import FilesTable from './filestable'

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

    return (
        <FilesTable config={this.props.config} files={this.state.files} />
    )
  }
}

Files.propTypes = {
  config: PropTypes.object,
}

