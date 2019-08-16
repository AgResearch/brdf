--
-- Name: stafffact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE stafffact FROM PUBLIC;
REVOKE ALL ON TABLE stafffact FROM agrbrdf;
GRANT ALL ON TABLE stafffact TO agrbrdf;
GRANT SELECT ON TABLE stafffact TO gbs;


