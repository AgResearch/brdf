--
-- Name: commentob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE commentob FROM PUBLIC;
REVOKE ALL ON TABLE commentob FROM agrbrdf;
GRANT ALL ON TABLE commentob TO agrbrdf;
GRANT SELECT ON TABLE commentob TO gbs;


