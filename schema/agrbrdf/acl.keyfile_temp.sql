--
-- Name: keyfile_temp; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE keyfile_temp FROM PUBLIC;
REVOKE ALL ON TABLE keyfile_temp FROM agrbrdf;
GRANT ALL ON TABLE keyfile_temp TO agrbrdf;
GRANT SELECT ON TABLE keyfile_temp TO gbs;


