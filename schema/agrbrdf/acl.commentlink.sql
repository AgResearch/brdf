--
-- Name: commentlink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE commentlink FROM PUBLIC;
REVOKE ALL ON TABLE commentlink FROM agrbrdf;
GRANT ALL ON TABLE commentlink TO agrbrdf;
GRANT SELECT ON TABLE commentlink TO gbs;


