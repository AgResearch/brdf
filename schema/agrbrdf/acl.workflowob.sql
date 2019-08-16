--
-- Name: workflowob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE workflowob FROM PUBLIC;
REVOKE ALL ON TABLE workflowob FROM agrbrdf;
GRANT ALL ON TABLE workflowob TO agrbrdf;
GRANT SELECT ON TABLE workflowob TO gbs;


